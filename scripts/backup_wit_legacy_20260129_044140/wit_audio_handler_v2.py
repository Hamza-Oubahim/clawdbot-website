#!/usr/bin/env python3
"""
Wit.ai Audio Handler v2 with Language Detection
Processes WhatsApp audio messages using appropriate Wit.ai API keys per language
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
        logging.FileHandler('/root/clawd/audio/wit_v2.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WitAudioHandlerV2:
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
        
        logger.info(f"Wit.ai Audio Handler v2 initialized")
        logger.info(f"Available languages: {[k for k, v in self.api_keys.items() if v]}")
        
        # Language detection fallback order
        self.language_fallback = ['fr', 'en', 'ar', 'default']
    
    def detect_language_from_audio(self, audio_path):
        """
        Try to detect language by testing with different API keys
        Returns the language code that gives the best result
        """
        logger.info(f"Detecting language for {audio_path}")
        
        # Convert to WAV first
        temp_dir = tempfile.gettempdir()
        wav_path = os.path.join(temp_dir, f"detect_{int(time.time())}.wav")
        
        try:
            # Convert to WAV
            cmd = ['ffmpeg', '-i', audio_path, '-ar', '16000', '-ac', '1', 
                   '-sample_fmt', 's16', wav_path, '-y', '-hide_banner', '-loglevel', 'error']
            subprocess.run(cmd, check=True, capture_output=True)
            
            # Read audio data
            with open(wav_path, 'rb') as f:
                audio_data = f.read()
            
            best_language = 'default'
            best_transcript = ""
            best_confidence = 0
            
            # Try each language API key
            for lang in ['fr', 'en', 'ar']:
                api_key = self.api_keys.get(lang)
                if not api_key:
                    continue
                
                try:
                    response = requests.post(
                        'https://api.wit.ai/speech',
                        headers={
                            'Authorization': f'Bearer {api_key}',
                            'Content-Type': 'audio/wav'
                        },
                        data=audio_data,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        # Parse response for transcript
                        transcript = self.extract_transcript_from_response(response.text)
                        if transcript:
                            # Simple confidence: longer transcript = more confident
                            confidence = len(transcript)
                            logger.info(f"Language {lang} detected transcript: {transcript[:50]}... (confidence: {confidence})")
                            
                            if confidence > best_confidence:
                                best_confidence = confidence
                                best_transcript = transcript
                                best_language = lang
                
                except Exception as e:
                    logger.debug(f"Language {lang} test failed: {e}")
                    continue
            
            logger.info(f"Detected language: {best_language} (confidence: {best_confidence})")
            return best_language
            
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            return 'default'
        
        finally:
            # Clean up
            if os.path.exists(wav_path):
                os.unlink(wav_path)
    
    def extract_transcript_from_response(self, response_text):
        """Extract transcript from Wit.ai NDJSON response"""
        response_text = response_text.replace('\r', '')
        lines = response_text.strip().split('\n')
        
        current_json = ""
        bracket_count = 0
        
        for line in lines:
            if not line.strip():
                continue
            
            current_json += line
            bracket_count += line.count('{') - line.count('}')
            
            if bracket_count == 0 and current_json.strip():
                try:
                    data = json.loads(current_json)
                    if 'text' in data and data.get('type') in ['FINAL_TRANSCRIPTION', 'FINAL_UNDERSTANDING']:
                        return data['text']
                except:
                    pass
                
                current_json = ""
                bracket_count = 0
        
        return ""
    
    def transcribe_audio_with_wit(self, audio_path, language='default'):
        """Transcribe audio file using appropriate Wit.ai API key"""
        
        # Select API key
        api_key = self.api_keys.get(language)
        if not api_key:
            # Fallback to default
            api_key = self.api_keys.get('default')
            language = 'default'
        
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
        
        # Process audio
        all_words = []
        full_transcript = ""
        
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
            
            # Extract transcript
            full_transcript = self.extract_transcript_from_response(response.text)
            
            if full_transcript:
                logger.info(f"Transcript: {full_transcript}")
            else:
                logger.warning(f"No transcript found in response")
                
                # Try to extract any text from response
                response_text = response.text.replace('\r', '')
                lines = response_text.strip().split('\n')
                for line in lines:
                    if '"text"' in line:
                        try:
                            # Simple extraction
                            start = line.find('"text"') + 8
                            end = line.find('",', start)
                            if end > start:
                                full_transcript = line[start:end]
                                logger.info(f"Extracted transcript: {full_transcript}")
                                break
                        except:
                            pass
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Wit.ai API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error processing audio: {e}")
            raise
        
        finally:
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
        """Process a single audio file with language detection"""
        try:
            filename = os.path.basename(filepath)
            logger.info(f"Processing audio file: {filename}")
            
            # Extract phone number and timestamp from filename
            parts = filename.split('_')
            if len(parts) >= 2:
                phone_number = parts[0]
                timestamp = parts[1].split('.')[0]
            else:
                phone_number = "unknown"
                timestamp = str(int(time.time()))
            
            # Detect language from audio content
            language = self.detect_language_from_audio(filepath)
            
            # Transcribe audio with detected language
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
            self.create_session_file(phone_number, result['transcript'], timestamp, result['language'])
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to process {filepath}: {e}")
            return False
    
    def create_session_file(self, phone_number, transcript, timestamp, language):
        """Create a session file for Clawdbot to read"""
        sessions_dir = '/root/clawd/sessions'
        os.makedirs(sessions_dir, exist_ok=True)
        
        session_filename = f"whatsapp_{phone_number}_{timestamp}.txt"
        session_path = os.path.join(sessions_dir, session_filename)
        
        session_content = f"""WhatsApp Audio Message
From: {phone_number}
Time: {datetime.fromtimestamp(int(timestamp)).isoformat() if timestamp.isdigit() else timestamp}
Language: {language}
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
    handler = WitAudioHandlerV2()
    
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