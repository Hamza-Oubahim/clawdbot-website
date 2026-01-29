#!/usr/bin/env python3
"""
Whisper Audio Processing Handler for Clawdbot WhatsApp Integration
Handles OGG voice notes, converts to WAV, transcribes with OpenAI Whisper API
"""

import os
import sys
import json
import tempfile
import subprocess
import requests
from pathlib import Path
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/root/clawd/audio/whisper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WhatsAppAudioProcessor:
    def __init__(self, openai_api_key=None):
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.audio_dir = "/root/clawd/audio"
        self.incoming_dir = os.path.join(self.audio_dir, "incoming")
        self.processed_dir = os.path.join(self.audio_dir, "processed")
        self.transcripts_dir = os.path.join(self.audio_dir, "transcripts")
        
        # Ensure directories exist
        for dir_path in [self.incoming_dir, self.processed_dir, self.transcripts_dir]:
            os.makedirs(dir_path, exist_ok=True)
    
    def convert_ogg_to_wav(self, ogg_path):
        """Convert OGG audio file to WAV format (required by Whisper)"""
        wav_path = ogg_path.replace('.ogg', '.wav')
        
        try:
            cmd = [
                'ffmpeg', '-i', ogg_path,
                '-ar', '16000',          # 16kHz sample rate
                '-ac', '1',              # Mono channel
                '-acodec', 'pcm_s16le',  # 16-bit PCM
                '-y',                    # Overwrite output
                wav_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"FFmpeg conversion failed: {result.stderr}")
                return None
            
            logger.info(f"Converted {ogg_path} to {wav_path}")
            return wav_path
            
        except Exception as e:
            logger.error(f"Conversion error: {e}")
            return None
    
    def transcribe_with_whisper(self, audio_path, language="ar"):
        """Transcribe audio using OpenAI Whisper API"""
        if not self.openai_api_key:
            logger.error("No OpenAI API key provided")
            return None
        
        try:
            import openai
            openai.api_key = self.openai_api_key
            
            with open(audio_path, "rb") as audio_file:
                transcript = openai.Audio.transcribe(
                    model="whisper-1",
                    file=audio_file,
                    language=language,  # Arabic (works reasonably for Darija)
                    response_format="text"
                )
            
            logger.info(f"Transcription successful: {len(transcript)} characters")
            return transcript
            
        except ImportError:
            logger.error("OpenAI library not installed. Run: pip install openai")
            return None
        except Exception as e:
            logger.error(f"Whisper API error: {e}")
            return None
    
    def process_audio_file(self, audio_path, sender_number=None):
        """Main processing pipeline for an audio file"""
        if not os.path.exists(audio_path):
            logger.error(f"Audio file not found: {audio_path}")
            return None
        
        # Extract filename and metadata
        filename = os.path.basename(audio_path)
        logger.info(f"Processing audio file: {filename}")
        
        # Convert OGG to WAV if needed
        if audio_path.endswith('.ogg'):
            wav_path = self.convert_ogg_to_wav(audio_path)
            if not wav_path:
                return None
        else:
            wav_path = audio_path
        
        # Transcribe with Whisper
        transcript = self.transcribe_with_whisper(wav_path, language="ar")
        
        if transcript:
            # Save transcript
            transcript_file = os.path.join(
                self.transcripts_dir, 
                f"{Path(audio_path).stem}.txt"
            )
            with open(transcript_file, 'w', encoding='utf-8') as f:
                f.write(transcript)
            
            # Move processed files
            processed_audio = os.path.join(self.processed_dir, filename)
            os.rename(audio_path, processed_audio)
            
            # Clean up temporary WAV file if it was converted
            if wav_path != audio_path and os.path.exists(wav_path):
                os.remove(wav_path)
            
            # Create metadata file
            metadata = {
                "original_file": filename,
                "sender": sender_number,
                "transcript": transcript,
                "processed_at": time.time(),
                "language": "ar"
            }
            
            metadata_file = transcript_file.replace('.txt', '.json')
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Processing complete. Transcript saved to {transcript_file}")
            return transcript
        
        return None
    
    def monitor_incoming_folder(self):
        """Monitor incoming folder for new audio files"""
        logger.info(f"Starting folder monitor on {self.incoming_dir}")
        
        processed_files = set()
        
        while True:
            try:
                # Check for new files
                for filename in os.listdir(self.incoming_dir):
                    if filename.endswith(('.ogg', '.mp3', '.wav', '.m4a')):
                        filepath = os.path.join(self.incoming_dir, filename)
                        
                        if filepath not in processed_files:
                            logger.info(f"New audio file detected: {filename}")
                            
                            # Extract sender from filename (format: sender_timestamp.ogg)
                            sender = None
                            if '_' in filename:
                                sender = filename.split('_')[0]
                            
                            # Process the file
                            transcript = self.process_audio_file(filepath, sender)
                            
                            if transcript:
                                # Send transcript to Clawdbot (via API or file)
                                self.send_to_clawdbot(transcript, sender)
                            
                            processed_files.add(filepath)
                
                time.sleep(5)  # Check every 5 seconds
                
            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                time.sleep(10)
    
    def send_to_clawdbot(self, transcript, sender_number):
        """Send transcript back to Clawdbot session"""
        try:
            # Method 1: Write to a file that Clawdbot can read
            session_file = f"/root/clawd/audio/session_{sender_number}.txt"
            with open(session_file, 'w', encoding='utf-8') as f:
                f.write(transcript)
            
            logger.info(f"Transcript written to session file: {session_file}")
            
            # Method 2: Send via Clawdbot API if available
            # self.send_via_api(transcript, sender_number)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send to Clawdbot: {e}")
            return False
    
    def send_via_api(self, transcript, sender_number):
        """Send transcript via Clawdbot API (if configured)"""
        # This would require Clawdbot API endpoint
        # For now, we'll use file-based communication
        pass

def main():
    """Main entry point"""
    processor = WhatsAppAudioProcessor()
    
    # Check if we have an API key
    if not processor.openai_api_key:
        logger.warning("OPENAI_API_KEY environment variable not set")
        logger.warning("Set it with: export OPENAI_API_KEY=your_key_here")
        logger.warning("Or pass it as argument: python whisper_handler.py --key YOUR_KEY")
    
    # Start monitoring
    processor.monitor_incoming_folder()

if __name__ == "__main__":
    main()