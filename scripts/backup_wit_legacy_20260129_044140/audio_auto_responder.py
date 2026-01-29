#!/usr/bin/env python3
"""
Audio Auto-Responder for Clawdbot
Reads transcribed audio session files and generates responses in the same language
"""

import os
import json
import time
import logging
import re
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/root/clawd/audio/auto_responder.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AudioAutoResponder:
    def __init__(self):
        self.sessions_dir = '/root/clawd/sessions'
        self.processed_dir = '/root/clawd/audio/processed_sessions'
        
        os.makedirs(self.sessions_dir, exist_ok=True)
        os.makedirs(self.processed_dir, exist_ok=True)
        
        # Language-specific response templates
        self.response_templates = {
            'ar': {
                'greeting': "وعليكم السلام! أنا بخير الحمد لله، شكراً لسؤالك. كيف يمكنني مساعدتك اليوم؟",
                'question': "شكراً لسؤالك. هل تحتاج إلى مساعدة إضافية؟",
                'request': "حسناً، سأحاول مساعدتك في هذا الأمر.",
                'default': "شكراً على رسالتك الصوتية. كيف يمكنني مساعدتك؟"
            },
            'fr': {
                'greeting': "Bonjour! Je vais bien, merci de demander. Comment puis-je vous aider aujourd'hui?",
                'question': "Merci pour votre question. Avez-vous besoin d'aide supplémentaire?",
                'request': "D'accord, je vais essayer de vous aider avec cela.",
                'default': "Merci pour votre message vocal. Comment puis-je vous aider?"
            },
            'en': {
                'greeting': "Hello! I'm doing well, thanks for asking. How can I help you today?",
                'question': "Thanks for your question. Do you need any additional help?",
                'request': "Alright, I'll try to help you with that.",
                'default': "Thanks for your voice message. How can I help you?"
            }
        }
        
        # Keywords for detecting intent in each language
        self.keywords = {
            'ar': {
                'greeting': ['السلام', 'مرحبا', 'اهلا', 'صباح الخير', 'مساء الخير'],
                'question': ['كيف', 'لماذا', 'متى', 'أين', 'ماذا', 'هل'],
                'request': ['بغيت', 'اريد', 'عاوز', 'نفسي', 'حاب', 'محتاج']
            },
            'fr': {
                'greeting': ['salut', 'bonjour', 'bonsoir', 'coucou', 'hello'],
                'question': ['comment', 'pourquoi', 'quand', 'où', 'quoi', 'est-ce'],
                'request': ['je veux', 'j\'ai besoin', 'je voudrais', 'peux-tu', 'pourrais-tu']
            },
            'en': {
                'greeting': ['hello', 'hi', 'hey', 'good morning', 'good afternoon'],
                'question': ['how', 'why', 'when', 'where', 'what', 'can you', 'could you'],
                'request': ['i want', 'i need', 'i would like', 'can you', 'could you']
            }
        }
    
    def detect_intent(self, text, language):
        """Detect the intent of the message"""
        text_lower = text.lower()
        
        if language in self.keywords:
            # Check for greetings
            for keyword in self.keywords[language]['greeting']:
                if keyword in text_lower:
                    return 'greeting'
            
            # Check for questions
            for keyword in self.keywords[language]['question']:
                if keyword in text_lower:
                    return 'question'
            
            # Check for requests
            for keyword in self.keywords[language]['request']:
                if keyword in text_lower:
                    return 'request'
        
        return 'default'
    
    def generate_response(self, text, language):
        """Generate a response in the same language"""
        if language not in self.response_templates:
            language = 'en'  # Default to English
        
        intent = self.detect_intent(text, language)
        response = self.response_templates[language][intent]
        
        # Personalize response if name is detected
        name = self.extract_name(text, language)
        if name:
            if language == 'ar':
                response = f"أهلاً {name}! " + response
            elif language == 'fr':
                response = f"Bonjour {name}! " + response
            elif language == 'en':
                response = f"Hi {name}! " + response
        
        return response
    
    def extract_name(self, text, language):
        """Try to extract a name from the text"""
        # Common names patterns
        if language == 'ar':
            # Arabic names
            arabic_names = ['صلاح', 'سارة', 'محمد', 'أحمد', 'علي', 'فاطمة', 'خالد']
            for name in arabic_names:
                if name in text:
                    return name
        elif language == 'fr':
            # French names
            french_names = ['sarah', 'jean', 'pierre', 'marie', 'paul', 'sophie']
            text_lower = text.lower()
            for name in french_names:
                if name in text_lower:
                    return name.capitalize()
        elif language == 'en':
            # English names
            english_names = ['sala', 'john', 'sarah', 'mike', 'emma', 'david']
            text_lower = text.lower()
            for name in english_names:
                if name in text_lower:
                    return name.capitalize()
        
        return None
    
    def process_session_file(self, filepath):
        """Process a session file and generate response"""
        try:
            logger.info(f"Processing session file: {filepath}")
            
            # Read session file
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse session file
            phone_number = None
            transcript = ""
            language = "en"  # Default
            
            lines = content.split('\n')
            for line in lines:
                if line.startswith('From:'):
                    phone_number = line.split(':')[1].strip()
                elif line.startswith('Language:'):
                    language = line.split(':')[1].strip()
                elif line.startswith('Transcript:'):
                    transcript = line.split(':', 1)[1].strip()
            
            if not transcript:
                logger.warning(f"No transcript found in {filepath}")
                return
            
            logger.info(f"Message from {phone_number} in {language}: {transcript[:100]}...")
            
            # Generate response in same language
            response = self.generate_response(transcript, language)
            logger.info(f"Generated response in {language}: {response}")
            
            # Send response via WhatsApp
            self.send_whatsapp_response(phone_number, response, language)
            
            # Move processed file
            filename = os.path.basename(filepath)
            processed_path = os.path.join(self.processed_dir, filename)
            os.rename(filepath, processed_path)
            logger.info(f"Moved to processed: {processed_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing {filepath}: {e}")
            return False
    
    def send_whatsapp_response(self, phone_number, message, language):
        """Send response via WhatsApp"""
        try:
            # Format phone number (remove + if present)
            if phone_number.startswith('+'):
                phone_number = phone_number[1:]
            
            # Create a response file for Clawdbot to send
            response_dir = '/root/clawd/whatsapp_responses'
            os.makedirs(response_dir, exist_ok=True)
            
            response_file = os.path.join(response_dir, f"response_{phone_number}_{int(time.time())}.txt")
            
            response_data = {
                "to": phone_number,
                "message": message,
                "language": language,
                "timestamp": time.time()
            }
            
            with open(response_file, 'w', encoding='utf-8') as f:
                json.dump(response_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Response queued for {phone_number}: {message[:50]}...")
            
            # Also log to a simple text file for easy monitoring
            log_file = '/root/clawd/audio/whatsapp_responses.log'
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"{time.ctime()} | {phone_number} | {language} | {message}\n")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to queue WhatsApp response: {e}")
            return False
    
    def start_monitoring(self):
        """Start monitoring session directory"""
        class SessionFileHandler(FileSystemEventHandler):
            def __init__(self, responder):
                self.responder = responder
            
            def on_created(self, event):
                if not event.is_directory and event.src_path.endswith('.txt'):
                    filepath = event.src_path
                    if 'whatsapp_' in os.path.basename(filepath):
                        logger.info(f"New session file detected: {filepath}")
                        # Wait a moment to ensure file is fully written
                        time.sleep(1)
                        self.responder.process_session_file(filepath)
        
        event_handler = SessionFileHandler(self)
        observer = Observer()
        observer.schedule(event_handler, self.sessions_dir, recursive=False)
        observer.start()
        
        logger.info(f"Started monitoring directory: {self.sessions_dir}")
        logger.info("Auto-responder ready! Will reply in same language as received.")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
            logger.info("Auto-responder stopped")
        
        observer.join()
    
    def test_responses(self):
        """Test response generation for all languages"""
        test_cases = [
            ("السلام عليكم صلاح", 'ar'),
            ("Salut Sarah, ça va?", 'fr'),
            ("Hey Sala, how are you?", 'en'),
            ("كيف حالك اليوم؟", 'ar'),
            ("Comment vas-tu aujourd'hui?", 'fr'),
            ("How are you doing today?", 'en'),
            ("بغيت ناخد عندك داك الصباط", 'ar'),
            ("Je veux prendre ces chaussures", 'fr'),
            ("I want to take those shoes", 'en')
        ]
        
        print("Testing auto-responder...")
        print("=" * 60)
        
        for text, lang in test_cases:
            response = self.generate_response(text, lang)
            print(f"Language: {lang}")
            print(f"Input: {text}")
            print(f"Response: {response}")
            print("-" * 60)

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Audio Auto-Responder")
    parser.add_argument('--test', action='store_true', help="Test response generation")
    parser.add_argument('--start', action='store_true', help="Start the auto-responder")
    
    args = parser.parse_args()
    
    responder = AudioAutoResponder()
    
    if args.test:
        responder.test_responses()
    elif args.start:
        # Process any existing session files first
        logger.info("Processing existing session files...")
        for filename in os.listdir(responder.sessions_dir):
            if filename.startswith('whatsapp_') and filename.endswith('.txt'):
                filepath = os.path.join(responder.sessions_dir, filename)
                responder.process_session_file(filepath)
        
        # Start monitoring
        responder.start_monitoring()
    else:
        print("Usage:")
        print("  --test    Test response generation")
        print("  --start   Start the auto-responder")
        print("\nRecommended: python audio_auto_responder.py --start")

if __name__ == "__main__":
    main()