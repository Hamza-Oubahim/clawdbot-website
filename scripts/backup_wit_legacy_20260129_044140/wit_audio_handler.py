#!/usr/bin/env python3
"""
Wit.ai Audio Handler for Clawdbot
Processes WhatsApp audio messages using Wit.ai speech-to-text API
"""

import os
import time
import json
import requests
import tempfile
import subprocess
import logging
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/root/clawd/audio/wit.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WitAudioHandler:
    def __init__(self):
        self.incoming_dir = '/root/clawd/audio/incoming'
        self.processed_dir = '/root/clawd/audio/processed'
        self.transcripts_dir = '/root/clawd/audio/transcripts'
        
        # Create directories if they don't exist
        for directory in [self.incoming_dir, self.processed_dir, self.transcripts_dir]:
            os.makedirs(directory, exist_ok=True)
        
        # Wit.ai API keys from environment
        self.api_keys = {
            'en': os.getenv('WIT_API_KEY_ENGLISH'),
            'ar': os.getenv('WIT_API_KEY_ARABIC'),
            'fr': os.getenv('WIT_API_KEY_FRENCH'),
            'default': os.getenv('WIT_API_KEY_DEFAULT')
        }
        
        logger.info(f"Wit.ai Audio Handler initialized")
        logger.info(f"Available languages: {[k for k, v in self.api_keys.items() if v]}")
    
    def detect_language_from_filename(self, filename):
        """Detect language from phone number or filename pattern"""
        # Moroccan numbers start with +212
        if '212' in filename:
            return 'ar'  # Arabic/Moroccan Darija
        return 'default'
    
    def transcribe_audio_with_wit(self, audio_path, language='default'):
        """Transcribe audio file using Wit.ai API"""
        
        # Select API key
        api_key = self.api_keys.get(language)
        if not api_key:
            api_key = self.api_keys.get('default')
        if not api_key:
            raise ValueError(f"No Wit.ai API key found for language: {language}")
        
        logger.info(f"Transcribing {audio_path} with language: {language}")
        
        # Check if file exists
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        # Convert to WAV if needed
        temp_dir = tempfile.gettempdir()
        final_audio_path = audio_path
        
        # Check file type and convert if necessary
        file_ext = Path(audio_path).suffix.lower()
        if file_ext not in ['.wav', '.wave']:
            logger.info(f"Converting {file_ext} to WAV format...")
            output_wav = os.path.join(temp_dir, f"converted_{int(time.time())}.wav")
            
            # Convert to 16kHz mono WAV (Wit.ai preferred format)
            cmd = ['ffmpeg', '-i', audio_path, '-ar', '16000', '-ac', '1', 
                   '-sample_fmt', 's16', output_wav, '-y', '-hide_banner', '-loglevel', 'error']
            
            try:
                subprocess.run(cmd, check=True, capture_output=True)
                final_audio_path = output_wav
                logger.info(f"Converted to WAV: {output_wav}")
            except subprocess.CalledProcessError as e:
                logger.error(f"FFmpeg conversion failed: {e.stderr.decode()}")
                raise
        
        # Check audio duration
        try:
            probe = subprocess.run(
                ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                 '-of', 'default=noprint_wrappers=1:nokey=1', final_audio_path],
                capture_output=True, text=True
            )
            duration_sec = float(probe.stdout.strip())
            logger.info(f"Audio duration: {duration_sec:.2f} seconds")
        except Exception as e:
            logger.warning(f"Could not get audio duration: {e}")
            duration_sec = 0
        
        # Wit.ai has a 20-second limit for free tier, so we need to chunk if longer
        CHUNK_DURATION = 15  # seconds
        all_words = []
        full_transcript = ""
        
        if duration_sec > 20:
            logger.info(f"Audio too long ({duration_sec}s), chunking into {CHUNK_DURATION}s segments...")
            
            # Create chunks
            chunk_pattern = os.path.join(temp_dir, f"chunk_%03d.wav")
            cmd = ['ffmpeg', '-i', final_audio_path, '-f', 'segment', 
                   '-segment_time', str(CHUNK_DURATION), '-c', 'copy', 
                   chunk_pattern, '-y', '-hide_banner', '-loglevel', 'error']
            
            try:
                subprocess.run(cmd, check=True, capture_output=True)
            except subprocess.CalledProcessError as e:
                logger.error(f"Chunking failed: {e.stderr.decode()}")
                raise
            
            # Get chunk files
            chunks = sorted([os.path.join(temp_dir, f) for f in os.listdir(temp_dir) 
                           if f.startswith("chunk_") and f.endswith(".wav")])
            
            logger.info(f"Created {len(chunks)} chunks")
            
            # Process each chunk
            for i, chunk_path in enumerate(chunks):
                time_offset_ms = i * CHUNK_DURATION * 1000
                logger.info(f"Processing chunk {i+1}/{len(chunks)}...")
                
                try:
                    with open(chunk_path, 'rb') as f:
                        audio_data = f.read()
                    
                    # Send to Wit.ai
                    response = requests.post(
                        'https://api.wit.ai/speech',
                        headers={
                            'Authorization': f'Bearer {api_key}',
                            'Content-Type': 'audio/wav'
                        },
                        data=audio_data,
                        timeout=30
                    )
                    
                    response.raise_for_status()
                    
                    # Parse Wit.ai NDJSON response (multiple JSON objects)
                    chunk_text = ""
                    responses_text = response.text
                    
                    # Clean up the response - remove any stray \r characters
                    responses_text = responses_text.replace('\r', '')
                    
                    # Split by newlines
                    lines = responses_text.strip().split('\n')
                    
                    # Parse each JSON object
                    current_json = ""
                    bracket_count = 0
                    
                    for line in lines:
                        if not line.strip():
                            continue
                        
                        # Handle multi-line JSON objects
                        current_json += line
                        bracket_count += line.count('{') - line.count('}')
                        
                        # If we have a complete JSON object
                        if bracket_count == 0 and current_json.strip():
                            try:
                                data = json.loads(current_json)
                                
                                # Check for FINAL_TRANSCRIPTION or FINAL_UNDERSTANDING
                                if 'text' in data and data.get('type') in ['FINAL_TRANSCRIPTION', 'FINAL_UNDERSTANDING']:
                                    chunk_text = data['text']
                                    full_transcript += chunk_text + " "
                                    logger.info(f"Chunk {i+1} transcript: {chunk_text}")
                                
                                # Also accept any text if we haven't found a final one yet
                                elif 'text' in data and not chunk_text:
                                    chunk_text = data['text']
                                    full_transcript += chunk_text + " "
                                    logger.info(f"Chunk {i+1} intermediate transcript: {chunk_text}")
                                
                                # Extract word-level timing if available
                                if 'speech' in data and 'tokens' in data['speech']:
                                    for token in data['speech']['tokens']:
                                        all_words.append({
                                            "text": token['token'],
                                            "startMs": token['start'] + time_offset_ms,
                                            "endMs": token['end'] + time_offset_ms,
                                            "confidence": token.get('confidence', 0),
                                            "speaker": 0
                                        })
                                
                            except json.JSONDecodeError as e:
                                logger.debug(f"Could not parse JSON: {e}")
                            
                            # Reset for next JSON object
                            current_json = ""
                            bracket_count = 0
                    
                except requests.exceptions.RequestException as e:
                    logger.error(f"Wit.ai API error for chunk {i+1}: {e}")
                except Exception as e:
                    logger.error(f"Error processing chunk {i+1}: {e}")
                finally:
                    # Clean up chunk file
                    try:
                        os.remove(chunk_path)
                    except:
                        pass
            
        else:
            # Process entire file if short enough
            logger.info("Processing entire audio file...")
            try:
                with open(final_audio_path, 'rb') as f:
                    audio_data = f.read()
                
                response = requests.post(
                    'https://api.wit.ai/speech',
                    headers={
                        'Authorization': f'Bearer {api_key}',
                        'Content-Type': 'audio/wav'
                    },
                    data=audio_data,
                    timeout=30
                )
                
                response.raise_for_status()
                
                # Parse Wit.ai NDJSON response
                responses_text = response.text
                full_transcript = ""
                
                # Clean up the response - remove any stray \r characters
                responses_text = responses_text.replace('\r', '')
                
                # Split by newlines
                lines = responses_text.strip().split('\n')
                
                # Parse each JSON object
                current_json = ""
                bracket_count = 0
                
                for line in lines:
                    if not line.strip():
                        continue
                    
                    # Handle multi-line JSON objects
                    current_json += line
                    bracket_count += line.count('{') - line.count('}')
                    
                    # If we have a complete JSON object
                    if bracket_count == 0 and current_json.strip():
                        try:
                            data = json.loads(current_json)
                            
                            # Check for FINAL_TRANSCRIPTION or FINAL_UNDERSTANDING
                            if 'text' in data and data.get('type') in ['FINAL_TRANSCRIPTION', 'FINAL_UNDERSTANDING']:
                                full_transcript = data['text']
                                logger.info(f"Full transcript: {full_transcript}")
                            
                            # Also accept any text if we haven't found a final one yet
                            elif 'text' in data and not full_transcript:
                                full_transcript = data['text']
                                logger.info(f"Intermediate transcript: {full_transcript}")
                            
                            # Extract word-level timing if available
                            if 'speech' in data and 'tokens' in data['speech']:
                                for token in data['speech']['tokens']:
                                    all_words.append({
                                        "text": token['token'],
                                        "startMs": token['start'],
                                        "endMs": token['end'],
                                        "confidence": token.get('confidence', 0),
                                        "speaker": 0
                                    })
                            
                        except json.JSONDecodeError as e:
                            logger.debug(f"Could not parse JSON: {e}")
                        
                        # Reset for next JSON object
                        current_json = ""
                        bracket_count = 0
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Wit.ai API error: {e}")
                raise
            except Exception as e:
                logger.error(f"Error processing audio: {e}")
                raise
        
        # Clean up converted file if we created one
        if final_audio_path != audio_path and os.path.exists(final_audio_path):
            try:
                os.remove(final_audio_path)
            except:
                pass
        
        return {
            "transcript": full_transcript.strip(),
            "language": language,
            "duration_seconds": duration_sec,
            "timestamp": datetime.now().isoformat()
        }
    
    def process_audio_file(self, filepath):
        """Process a single audio file"""
        try:
            filename = os.path.basename(filepath)
            logger.info(f"Processing audio file: {filename}")
            
            # Extract phone number and timestamp from filename
            # Format: PHONE_NUMBER_TIMESTAMP.ogg
            parts = filename.split('_')
            if len(parts) >= 2:
                phone_number = parts[0]
                timestamp = parts[1].split('.')[0]
            else:
                phone_number = "unknown"
                timestamp = str(int(time.time()))
            
            # Detect language
            language = self.detect_language_from_filename(filename)
            
            # Transcribe audio
            result = self.transcribe_audio_with_wit(filepath, language)
            
            # Save transcript
            transcript_filename = f"{phone_number}_{timestamp}.txt"
            transcript_path = os.path.join(self.transcripts_dir, transcript_filename)
            
            with open(transcript_path, 'w', encoding='utf-8') as f:
                f.write(result['transcript'])
            
            # Save metadata
            metadata_filename = f"{phone_number}_{timestamp}.json"
            metadata_path = os.path.join(self.transcripts_dir, metadata_filename)
            
            metadata = {
                "phone_number": phone_number,
                "timestamp": timestamp,
                "original_filename": filename,
                "transcript_filename": transcript_filename,
                **result
            }
            
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            # Move processed file
            processed_path = os.path.join(self.processed_dir, filename)
            os.rename(filepath, processed_path)
            
            logger.info(f"Successfully processed {filename}")
            logger.info(f"Transcript saved to {transcript_path}")
            
            # Create session file for Clawdbot
            self.create_session_file(phone_number, result['transcript'], timestamp)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to process {filepath}: {e}")
            return False
    
    def create_session_file(self, phone_number, transcript, timestamp):
        """Create a session file for Clawdbot to read"""
        sessions_dir = '/root/clawd/sessions'
        os.makedirs(sessions_dir, exist_ok=True)
        
        session_filename = f"whatsapp_{phone_number}_{timestamp}.txt"
        session_path = os.path.join(sessions_dir, session_filename)
        
        session_content = f"""WhatsApp Audio Message
From: {phone_number}
Time: {datetime.fromtimestamp(int(timestamp)).isoformat() if timestamp.isdigit() else timestamp}
Transcript: {transcript}
"""
        
        with open(session_path, 'w', encoding='utf-8') as f:
            f.write(session_content)
        
        logger.info(f"Session file created: {session_path}")
    
    def start_monitoring(self):
        """Start monitoring the incoming directory for new audio files"""
        class AudioFileHandler(FileSystemEventHandler):
            def __init__(self, processor):
                self.processor = processor
            
            def on_created(self, event):
                if not event.is_directory:
                    filepath = event.src_path
                    if filepath.endswith(('.ogg', '.mp3', '.wav', '.m4a', '.flac')):
                        logger.info(f"New audio file detected: {filepath}")
                        # Wait a moment to ensure file is fully written
                        time.sleep(1)
                        self.processor.process_audio_file(filepath)
        
        event_handler = AudioFileHandler(self)
        observer = Observer()
        observer.schedule(event_handler, self.incoming_dir, recursive=False)
        observer.start()
        
        logger.info(f"Started monitoring directory: {self.incoming_dir}")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
            logger.info("Stopping monitoring...")
        
        observer.join()

def main():
    """Main function"""
    handler = WitAudioHandler()
    
    # Check if we have at least one API key
    if not any(handler.api_keys.values()):
        logger.error("No Wit.ai API keys found in environment variables!")
        logger.error("Please set at least one of:")
        logger.error("  WIT_API_KEY_ENGLISH")
        logger.error("  WIT_API_KEY_ARABIC")
        logger.error("  WIT_API_KEY_FRENCH")
        logger.error("  WIT_API_KEY_DEFAULT")
        return
    
    # Process any existing files
    logger.info("Processing existing files in incoming directory...")
    for filename in os.listdir(handler.incoming_dir):
        if filename.endswith(('.ogg', '.mp3', '.wav', '.m4a', '.flac')):
            filepath = os.path.join(handler.incoming_dir, filename)
            handler.process_audio_file(filepath)
    
    # Start monitoring for new files
    handler.start_monitoring()

if __name__ == "__main__":
    main()