#!/usr/bin/env python3
"""
Clawdbot Audio Integration Bridge
Connects audio transcripts back into Clawdbot sessions
"""

import os
import sys
import json
import time
import logging
import subprocess
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TranscriptHandler(FileSystemEventHandler):
    """Watch for new transcript files and inject them into Clawdbot"""
    
    def __init__(self, transcripts_dir):
        self.transcripts_dir = transcripts_dir
        self.processed_files = set()
    
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith('.txt'):
            self.process_transcript(event.src_path)
    
    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith('.txt'):
            self.process_transcript(event.src_path)
    
    def process_transcript(self, transcript_path):
        """Process a new transcript file"""
        if transcript_path in self.processed_files:
            return
        
        try:
            logger.info(f"New transcript detected: {transcript_path}")
            
            # Read transcript
            with open(transcript_path, 'r', encoding='utf-8') as f:
                transcript = f.read().strip()
            
            if not transcript:
                logger.warning(f"Empty transcript: {transcript_path}")
                return
            
            # Extract sender from filename (format: sender_timestamp.txt)
            filename = Path(transcript_path).stem
            parts = filename.split('_')
            sender = parts[0] if len(parts) > 1 else "unknown"
            
            # Read metadata if available
            metadata_path = transcript_path.replace('.txt', '.json')
            metadata = {}
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                sender = metadata.get('sender', sender)
            
            logger.info(f"Transcript from {sender}: {transcript[:100]}...")
            
            # Inject into Clawdbot session
            self.inject_to_clawdbot(sender, transcript, metadata)
            
            # Mark as processed
            self.processed_files.add(transcript_path)
            
            # Move to processed folder
            processed_dir = os.path.join(os.path.dirname(transcript_path), "..", "processed_transcripts")
            os.makedirs(processed_dir, exist_ok=True)
            
            processed_path = os.path.join(processed_dir, os.path.basename(transcript_path))
            os.rename(transcript_path, processed_path)
            
            logger.info(f"Moved transcript to: {processed_path}")
            
        except Exception as e:
            logger.error(f"Error processing transcript {transcript_path}: {e}")
    
    def inject_to_clawdbot(self, sender_number, transcript, metadata=None):
        """Inject transcript into Clawdbot session"""
        try:
            # Method 1: Direct session injection via Clawdbot API
            self.inject_via_api(sender_number, transcript, metadata)
            
            # Method 2: Create session file for Clawdbot to read
            self.create_session_file(sender_number, transcript, metadata)
            
            # Method 3: Send via WhatsApp message (if configured)
            self.send_whatsapp_response(sender_number, transcript, metadata)
            
            return True
            
        except Exception as e:
            logger.error(f"Injection error: {e}")
            return False
    
    def inject_via_api(self, sender_number, transcript, metadata):
        """Inject via Clawdbot REST API"""
        # This requires Clawdbot API to be enabled
        # For now, we'll use file-based method
        pass
    
    def create_session_file(self, sender_number, transcript, metadata):
        """Create a session file that Clawdbot can read"""
        session_dir = "/root/clawd/sessions"
        os.makedirs(session_dir, exist_ok=True)
        
        # Format: WhatsApp session key
        session_key = f"whatsapp:{sender_number}"
        session_file = os.path.join(session_dir, f"audio_{sender_number}_{int(time.time())}.txt")
        
        session_data = {
            "session_key": session_key,
            "message": transcript,
            "source": "audio_transcription",
            "timestamp": time.time(),
            "metadata": metadata or {}
        }
        
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Session file created: {session_file}")
        
        # Also create a simple text file for easy reading
        text_file = session_file.replace('.txt', '_text.txt')
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(f"[Audio Transcription from {sender_number}]\n")
            f.write(f"Time: {time.ctime()}\n")
            f.write(f"Transcript: {transcript}\n")
        
        return session_file
    
    def send_whatsapp_response(self, sender_number, transcript, metadata):
        """Send acknowledgment via WhatsApp"""
        # This would require WhatsApp Business API integration
        # For now, we'll just log it
        logger.info(f"Would send WhatsApp response to {sender_number}")
        
        # Example response
        response = f"✅ تمت معالجة الملف الصوتي وتحويله إلى نص:\n\n{transcript[:500]}..."
        if len(transcript) > 500:
            response += "\n\n(النص مقصوص للعرض)"
        
        logger.info(f"Response: {response}")
        return response

class ClawdbotAudioBridge:
    """Main bridge between audio processing and Clawdbot"""
    
    def __init__(self):
        self.audio_dir = "/root/clawd/audio"
        self.transcripts_dir = os.path.join(self.audio_dir, "transcripts")
        self.sessions_dir = "/root/clawd/sessions"
        
        os.makedirs(self.transcripts_dir, exist_ok=True)
        os.makedirs(self.sessions_dir, exist_ok=True)
        
        self.observer = Observer()
        self.handler = TranscriptHandler(self.transcripts_dir)
    
    def start(self):
        """Start the bridge service"""
        logger.info("Starting Clawdbot Audio Bridge...")
        logger.info(f"Monitoring: {self.transcripts_dir}")
        logger.info(f"Sessions: {self.sessions_dir}")
        
        # Start file system observer
        self.observer.schedule(self.handler, self.transcripts_dir, recursive=False)
        self.observer.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()
            logger.info("Bridge stopped by user")
        
        self.observer.join()
    
    def test_integration(self):
        """Test the integration"""
        logger.info("Testing integration...")
        
        # Create a test transcript
        test_transcript = "هذا اختبار لنظام معالجة الصوت بالدارجة المغربية. النظام يعمل بشكل جيد."
        test_sender = "212635278125"
        
        test_file = os.path.join(self.transcripts_dir, f"{test_sender}_{int(time.time())}.txt")
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_transcript)
        
        logger.info(f"Test transcript created: {test_file}")
        
        # Wait for processing
        time.sleep(2)
        
        # Check if session file was created
        session_files = [f for f in os.listdir(self.sessions_dir) if f.startswith('audio_')]
        if session_files:
            logger.info(f"Session files created: {session_files}")
            return True
        else:
            logger.warning("No session files created")
            return False

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Clawdbot Audio Integration Bridge")
    parser.add_argument('--test', action='store_true', help="Run integration test")
    parser.add_argument('--start', action='store_true', help="Start the bridge service")
    parser.add_argument('--wit-mode', action='store_true', help="Run in Wit.ai mode")
    
    args = parser.parse_args()
    
    bridge = ClawdbotAudioBridge()
    
    if args.test:
        bridge.test_integration()
    elif args.start or args.wit_mode:
        bridge.start()
    else:
        print("Usage:")
        print("  --test        Run integration test")
        print("  --start       Start the bridge service")
        print("  --wit-mode    Start in Wit.ai mode")
        print("\nRecommended: python clawdbot_integration.py --wit-mode")

if __name__ == "__main__":
    main()