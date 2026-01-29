#!/usr/bin/env python3
"""
Wit.ai Audio Processor - Main Entry Point
Uses global Clawdbot environment variables for API keys
"""

import os
import sys
import json
import logging
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from core.wit_handler import WitAudioProcessor
from core.file_monitor import AudioFileMonitor
from utils.config_loader import load_config

def setup_logging(config):
    """Configure logging based on config"""
    log_dir = Path(__file__).parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    
    log_level = getattr(logging, config.get('log_level', 'INFO').upper())
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / 'wit_processor.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def check_environment(config):
    """Check required environment variables from global Clawdbot env"""
    logger = logging.getLogger(__name__)
    
    # Check for Wit.ai API keys in global environment
    wit_keys_found = []
    for env_var in ['WIT_API_KEY_ENGLISH', 'WIT_API_KEY_ARABIC', 'WIT_API_KEY_FRENCH']:
        if os.getenv(env_var):
            wit_keys_found.append(env_var)
    
    if not wit_keys_found:
        logger.error("No Wit.ai API keys found in global environment!")
        logger.info("Required environment variables (at least one):")
        logger.info("  WIT_API_KEY_ENGLISH, WIT_API_KEY_ARABIC, or WIT_API_KEY_FRENCH")
        logger.info("")
        logger.info("Current global environment has:")
        for key in ['OPENAI_API_KEY', 'GEMINI_API_KEY', 'DEEPSEEK_API_KEY']:
            if os.getenv(key):
                logger.info(f"  ✓ {key}: Present")
            else:
                logger.info(f"  ✗ {key}: Missing")
        return False
    
    logger.info(f"Found Wit.ai API keys in global environment: {wit_keys_found}")
    
    # Check for other API keys (for reference)
    other_keys = ['OPENAI_API_KEY', 'GEMINI_API_KEY', 'DEEPSEEK_API_KEY']
    for key in other_keys:
        if os.getenv(key):
            logger.debug(f"Global {key} available")
    
    return True

def main():
    """Main function"""
    global logger
    
    # Load configuration
    config = load_config()
    logger = setup_logging(config)
    
    logger.info("=" * 60)
    logger.info("Wit.ai Audio Processor Starting")
    logger.info("Using Global Clawdbot Environment")
    logger.info("=" * 60)
    
    # Check environment
    if not check_environment(config):
        return 1
    
    # Initialize processor
    try:
        processor = WitAudioProcessor(config)
        monitor = AudioFileMonitor(
            processor=processor,
            incoming_dir=config['directories']['incoming'],
            processed_dir=config['directories']['processed']
        )
        
        logger.info(f"Monitoring directory: {config['directories']['incoming']}")
        logger.info(f"Available languages: {list(processor.api_keys.keys())}")
        
        # Log API key status (masked)
        for lang, key in processor.api_keys.items():
            if key:
                masked = f"{key[:4]}...{key[-4:]}"
                logger.info(f"  {lang}: {masked}")
        
        # Start monitoring
        monitor.start()
        
    except KeyboardInterrupt:
        logger.info("Shutdown requested...")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1
    finally:
        if 'monitor' in locals():
            monitor.stop()
        logger.info("Wit.ai Audio Processor stopped")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())