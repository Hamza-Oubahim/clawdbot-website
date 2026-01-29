#!/usr/bin/env python3
"""
Main entry point for example-audio-project
"""

import os
import sys
import json
import logging
from pathlib import Path

def setup_logging():
    """Configure logging"""
    log_dir = Path(__file__).parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / 'app.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def load_config():
    """Load configuration from config/settings.json"""
    config_path = Path(__file__).parent.parent / "config" / "settings.json"
    with open(config_path, 'r') as f:
        return json.load(f)

def main():
    """Main function"""
    logger = setup_logging()
    config = load_config()
    
    logger.info(f"Starting {config['project_name']} v{config['version']}")
    logger.info(f"Description: {config['description']}")
    
    # Your main logic here
    logger.info("Project is running!")
    
    # Example: Process something
    logger.info("Processing complete")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
