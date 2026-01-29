#!/usr/bin/env python3
"""
WhatsApp Webhook Simulator for testing audio processing
Simulates receiving voice notes from WhatsApp API
"""

import os
import sys
import json
import time
import shutil
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WhatsAppSimulator:
    def __init__(self):
        self.audio_dir = "/root/clawd/audio"
        self.incoming_dir = os.path.join(self.audio_dir, "incoming")
        self.sample_dir = os.path.join(self.audio_dir, "samples")
        
        os.makedirs(self.incoming_dir, exist_ok=True)
        os.makedirs(self.sample_dir, exist_ok=True)
    
    def simulate_voice_note(self, sender_number, audio_file_path=None):
        """Simulate receiving a voice note from WhatsApp"""
        timestamp = int(time.time())
        
        if audio_file_path and os.path.exists(audio_file_path):
            # Copy existing audio file
            filename = f"{sender_number}_{timestamp}.ogg"
            dest_path = os.path.join(self.incoming_dir, filename)
            shutil.copy2(audio_file_path, dest_path)
            logger.info(f"Simulated voice note from {sender_number}: {filename}")
            return dest_path
        else:
            # Create a dummy file for testing
            filename = f"{sender_number}_{timestamp}.ogg"
            dummy_path = os.path.join(self.incoming_dir, filename)
            
            # Create a small dummy OGG file (just header)
            with open(dummy_path, 'wb') as f:
                f.write(b'OGG_SIMULATED_AUDIO')  # Not a real OGG, but for testing
            
            logger.info(f"Created dummy voice note from {sender_number}: {filename}")
            return dummy_path
    
    def simulate_webhook_payload(self, sender_number, media_id="media_12345", wit_mode=False):
        """Simulate WhatsApp webhook JSON payload"""
        payload = {
            "object": "whatsapp_business_account",
            "entry": [{
                "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
                "changes": [{
                    "value": {
                        "messaging_product": "whatsapp",
                        "metadata": {
                            "display_phone_number": "1234567890",
                            "phone_number_id": "PHONE_NUMBER_ID"
                        },
                        "contacts": [{
                            "profile": {"name": "Test User"},
                            "wa_id": sender_number
                        }],
                        "messages": [{
                            "from": sender_number,
                            "id": f"wamid.{int(time.time())}",
                            "timestamp": str(int(time.time())),
                            "type": "audio",
                            "audio": {
                                "id": media_id,
                                "mime_type": "audio/ogg; codecs=opus"
                            }
                        }]
                    },
                    "field": "messages"
                }]
            }]
        }
        
        payload_file = os.path.join(self.incoming_dir, f"webhook_{sender_number}_{int(time.time())}.json")
        with open(payload_file, 'w') as f:
            json.dump(payload, f, indent=2)
        
        logger.info(f"Webhook payload saved: {payload_file}")
        return payload
    
    def create_test_environment(self):
        """Create test files and environment"""
        # Create sample audio files directory
        samples = [
            "test_short.ogg",
            "test_medium.ogg", 
            "test_long.ogg"
        ]
        
        for sample in samples:
            sample_path = os.path.join(self.sample_dir, sample)
            if not os.path.exists(sample_path):
                with open(sample_path, 'wb') as f:
                    f.write(f"DUMMY_AUDIO_{sample}".encode())
        
        # Create configuration file
        config = {
            "whatsapp": {
                "webhook_url": "http://localhost:8080/webhook",
                "verify_token": "clawdbot_audio_test",
                "access_token": "TEST_ACCESS_TOKEN"
            },
            "openai": {
                "api_key_env": "OPENAI_API_KEY",
                "model": "whisper-1",
                "language": "ar"
            },
            "audio_processing": {
                "incoming_dir": self.incoming_dir,
                "processed_dir": os.path.join(self.audio_dir, "processed"),
                "transcripts_dir": os.path.join(self.audio_dir, "transcripts"),
                "max_file_size_mb": 16
            }
        }
        
        config_file = os.path.join(self.audio_dir, "config.json")
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"Test environment created in {self.audio_dir}")
        logger.info(f"Configuration: {config_file}")
        
        return config_file

def main():
    """Test the simulator"""
    import argparse
    
    parser = argparse.ArgumentParser(description="WhatsApp Webhook Simulator")
    parser.add_argument('--wit', action='store_true', help="Test Wit.ai mode")
    args = parser.parse_args()
    
    simulator = WhatsAppSimulator()
    
    print("WhatsApp Audio Processing Simulator")
    print("=" * 50)
    
    # Create test environment
    config_file = simulator.create_test_environment()
    
    # Simulate voice notes from different senders
    senders = ["212626474248", "212635278125"]
    
    for sender in senders:
        print(f"\nSimulating voice note from {sender}:")
        
        # Simulate webhook payload
        payload = simulator.simulate_webhook_payload(sender, wit_mode=args.wit)
        
        # Simulate audio file
        audio_file = simulator.simulate_voice_note(sender)
        
        print(f"  • Webhook payload created")
        print(f"  • Audio file: {audio_file}")
    
    if args.wit:
        print("\n" + "=" * 50)
        print("Wit.ai Mode Test")
        print("=" * 50)
        print("Next steps:")
        print("1. Set WIT_API_KEY_DEFAULT environment variable")
        print("2. Run: bash /root/clawd/scripts/start_wit_audio_processing.sh")
        print("3. The handler will process files in /root/clawd/audio/incoming")
        print("4. Transcripts will be saved to /root/clawd/audio/transcripts")
        
        # Create a test script for Wit.ai
        test_script = """#!/bin/bash
# Test script for Wit.ai audio processing

export WIT_API_KEY_DEFAULT="your_wit_ai_api_key_here"

# Start the Wit.ai audio processing system
bash /root/clawd/scripts/start_wit_audio_processing.sh

echo "Wit.ai test environment ready!"
echo "Check logs in /root/clawd/audio/wit.log"
"""
    else:
        print("\n" + "=" * 50)
        print("OpenAI Whisper Mode Test")
        print("=" * 50)
        print("Next steps:")
        print("1. Set OPENAI_API_KEY environment variable")
        print("2. Run: python /root/clawd/scripts/whisper_handler.py")
        print("3. The handler will process files in /root/clawd/audio/incoming")
        print("4. Transcripts will be saved to /root/clawd/audio/transcripts")
        
        # Create a test script for Whisper
        test_script = """#!/bin/bash
# Test script for audio processing

export OPENAI_API_KEY="your_openai_api_key_here"

# Start the whisper handler in background
python3 /root/clawd/scripts/whisper_handler.py &

# Simulate incoming voice notes
python3 /root/clawd/scripts/whatsapp_simulator.py

echo "Test environment ready!"
echo "Check logs in /root/clawd/audio/whisper.log"
"""
    
    test_file = "/root/clawd/scripts/test_audio_processing.sh"
    with open(test_file, 'w') as f:
        f.write(test_script)
    
    os.chmod(test_file, 0o755)
    print(f"\nTest script created: {test_file}")

if __name__ == "__main__":
    main()