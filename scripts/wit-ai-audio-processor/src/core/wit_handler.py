"""
Wit.ai Audio Processor Core
Handles audio file processing and Wit.ai API communication
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
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class WitAudioProcessor:
    """Main Wit.ai audio processing class"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Setup directories
        self.incoming_dir = Path(config['directories']['incoming'])
        self.processed_dir = Path(config['directories']['processed'])
        self.transcripts_dir = Path(config['directories']['transcripts'])
        
        # Create directories
        for directory in [self.incoming_dir, self.processed_dir, self.transcripts_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # API keys
        self.api_keys = config.get('api_keys', {})
        
        # Processing settings
        self.max_audio_duration = config['processing']['max_audio_duration']
        self.chunk_duration = config['processing']['chunk_duration']
        
        logger.info(f"WitAudioProcessor initialized with {len(self.api_keys)} API keys")
        logger.info(f"Directories: incoming={self.incoming_dir}, processed={self.processed_dir}")
    
    def process_audio_file(self, filepath: Path) -> bool:
        """Process a single audio file"""
        try:
            logger.info(f"Processing audio file: {filepath.name}")
            
            # Extract metadata from filename
            metadata = self.extract_metadata_from_filename(filepath.name)
            
            # Detect language
            language = self.detect_language(metadata.get('phone_number'), filepath)
            logger.info(f"Detected language: {language} for phone: {metadata.get('phone_number')}")
            
            # Convert audio to WAV if needed
            wav_path = self.convert_to_wav(filepath)
            if not wav_path:
                logger.error(f"Failed to convert {filepath.name} to WAV")
                return False
            
            # Process audio with Wit.ai
            transcript = self.process_with_wit(wav_path, language)
            
            if transcript:
                # Save transcript
                self.save_transcript(filepath.name, transcript, metadata, language)
                
                # Create session file for Clawdbot
                self.create_session_file(filepath.name, transcript, metadata)
                
                # Move processed file
                self.move_processed_file(filepath)
                
                logger.info(f"Successfully processed {filepath.name}")
                return True
            else:
                logger.error(f"Failed to get transcript for {filepath.name}")
                return False
                
        except Exception as e:
            logger.error(f"Error processing {filepath.name}: {e}", exc_info=True)
            return False
    
    def extract_metadata_from_filename(self, filename: str) -> Dict[str, Any]:
        """Extract phone number and timestamp from filename"""
        # Expected format: 212626474248_1706461200.ogg
        metadata = {
            'phone_number': None,
            'timestamp': None,
            'original_filename': filename
        }
        
        try:
            # Remove extension
            name_without_ext = os.path.splitext(filename)[0]
            
            # Split by underscore
            parts = name_without_ext.split('_')
            if len(parts) >= 2:
                metadata['phone_number'] = parts[0]
                metadata['timestamp'] = parts[1]
            
            # Try to parse timestamp
            if metadata['timestamp']:
                try:
                    ts = float(metadata['timestamp'])
                    metadata['datetime'] = datetime.fromtimestamp(ts).isoformat()
                except (ValueError, TypeError):
                    metadata['datetime'] = metadata['timestamp']
        
        except Exception as e:
            logger.warning(f"Could not parse metadata from {filename}: {e}")
        
        return metadata
    
    def detect_language(self, phone_number: Optional[str], audio_path: Path) -> str:
        """Detect language from phone number or audio content"""
        # Default language
        language = 'default'
        
        # Detect from phone number (Moroccan numbers start with 212)
        if phone_number and phone_number.startswith('212'):
            language = 'ar'  # Arabic/Moroccan Darija
        elif phone_number:
            # For other numbers, try to detect from available API keys
            available_langs = list(self.api_keys.keys())
            if 'en' in available_langs and 'default' in available_langs:
                language = 'en'  # Prefer English over default if available
        
        # Check if we have API key for detected language
        if language not in self.api_keys:
            # Fall back to default
            if 'default' in self.api_keys:
                language = 'default'
            elif self.api_keys:
                # Use first available key
                language = list(self.api_keys.keys())[0]
            else:
                raise ValueError("No Wit.ai API keys available")
        
        return language
    
    def convert_to_wav(self, audio_path: Path) -> Optional[Path]:
        """Convert audio file to WAV format (16kHz mono)"""
        try:
            # Create temp file for WAV output
            temp_dir = tempfile.gettempdir()
            wav_filename = f"{audio_path.stem}_converted.wav"
            wav_path = Path(temp_dir) / wav_filename
            
            # Convert using ffmpeg
            cmd = [
                'ffmpeg', '-i', str(audio_path),
                '-ar', '16000',          # 16kHz sample rate
                '-ac', '1',              # Mono
                '-acodec', 'pcm_s16le',  # 16-bit PCM
                '-y',                    # Overwrite output
                str(wav_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"FFmpeg conversion failed: {result.stderr}")
                return None
            
            if wav_path.exists() and wav_path.stat().st_size > 0:
                logger.debug(f"Converted to WAV: {wav_path}")
                return wav_path
            else:
                logger.error(f"WAV file not created or empty: {wav_path}")
                return None
                
        except Exception as e:
            logger.error(f"Audio conversion error: {e}")
            return None
    
    def process_with_wit(self, wav_path: Path, language: str) -> Optional[str]:
        """Send audio to Wit.ai API and get transcript"""
        api_key = self.api_keys.get(language)
        if not api_key:
            logger.error(f"No API key for language: {language}")
            return None
        
        try:
            # Read audio file
            with open(wav_path, 'rb') as audio_file:
                audio_data = audio_file.read()
            
            # Prepare request
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'audio/wav'
            }
            
            # Send to Wit.ai
            logger.debug(f"Sending {wav_path.name} to Wit.ai ({language})")
            response = requests.post(
                'https://api.wit.ai/speech',
                headers=headers,
                data=audio_data,
                timeout=30
            )
            
            if response.status_code == 200:
                transcript = self.extract_transcript(response.text)
                logger.debug(f"Wit.ai response: {transcript[:100]}...")
                return transcript
            else:
                logger.error(f"Wit.ai API error: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error calling Wit.ai: {e}")
            return None
        except Exception as e:
            logger.error(f"Error processing with Wit.ai: {e}")
            return None
    
    def extract_transcript(self, response_text: str) -> str:
        """Extract transcript from Wit.ai NDJSON response"""
        try:
            # Wit.ai returns NDJSON (newline-delimited JSON)
            lines = response_text.strip().split('\n')
            transcripts = []
            
            for line in lines:
                if line:
                    data = json.loads(line)
                    if 'text' in data:
                        transcripts.append(data['text'].strip())
            
            # Combine all transcript parts
            full_transcript = ' '.join(transcripts)
            return full_transcript if full_transcript else "[No speech detected]"
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Wit.ai response: {e}")
            return f"[Error parsing response: {response_text[:100]}...]"
    
    def save_transcript(self, original_filename: str, transcript: str, 
                       metadata: Dict[str, Any], language: str):
        """Save transcript and metadata to file"""
        try:
            # Create transcript data
            transcript_data = {
                'filename': original_filename,
                'transcript': transcript,
                'language': language,
                'metadata': metadata,
                'processed_at': datetime.now().isoformat()
            }
            
            # Save as JSON
            transcript_filename = f"{os.path.splitext(original_filename)[0]}.json"
            transcript_path = self.transcripts_dir / transcript_filename
            
            with open(transcript_path, 'w', encoding='utf-8') as f:
                json.dump(transcript_data, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Transcript saved: {transcript_path}")
            
        except Exception as e:
            logger.error(f"Failed to save transcript: {e}")
    
    def create_session_file(self, original_filename: str, transcript: str, 
                           metadata: Dict[str, Any]):
        """Create session file for Clawdbot to read"""
        try:
            # Create session directory if it doesn't exist
            session_dir = Path(self.config['directories']['sessions'])
            session_dir.mkdir(parents=True, exist_ok=True)
            
            # Create session filename
            session_filename = f"wit_{metadata.get('phone_number', 'unknown')}_{int(time.time())}.txt"
            session_path = session_dir / session_filename
            
            # Format message for Clawdbot
            phone_display = metadata.get('phone_number', 'Unknown')
            time_display = metadata.get('datetime', 'Unknown time')
            
            message = f"📱 Audio message from {phone_display} at {time_display}:\n\n"
            message += f"{transcript}\n\n"
            message += f"(Transcribed via Wit.ai)"
            
            # Write session file
            with open(session_path, 'w', encoding='utf-8') as f:
                f.write(message)
            
            logger.debug(f"Session file created: {session_path}")
            
        except Exception as e:
            logger.error(f"Failed to create session file: {e}")
    
    def move_processed_file(self, filepath: Path):
        """Move processed file to processed directory"""
        try:
            destination = self.processed_dir / filepath.name
            filepath.rename(destination)
            logger.debug(f"Moved to processed: {destination}")
        except Exception as e:
            logger.error(f"Failed to move processed file: {e}")