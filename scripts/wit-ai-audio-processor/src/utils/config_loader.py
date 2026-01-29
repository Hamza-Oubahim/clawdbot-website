"""
Configuration loader for Wit.ai Audio Processor
Uses global Clawdbot environment variables
"""

import os
import json
from pathlib import Path
from typing import Dict, Any

def load_config() -> Dict[str, Any]:
    """Load configuration from config/settings.json and global environment"""
    config_path = Path(__file__).parent.parent.parent / "config" / "settings.json"
    
    # Load base config
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Update config with global environment variables
    update_config_from_global_env(config)
    
    return config

def update_config_from_global_env(config: Dict[str, Any]):
    """Update configuration with global environment variables"""
    
    # Use global environment (no .env file needed)
    if config.get('environment', {}).get('use_global_env', True):
        # Map global environment variables to API keys
        api_keys = {}
        env_mappings = config.get('environment', {}).get('api_key_mapping', {})
        
        for env_var, lang_code in env_mappings.items():
            if os.getenv(env_var):
                if lang_code in ['en', 'ar', 'fr']:  # Wit.ai language codes
                    api_keys[lang_code] = os.getenv(env_var)
        
        # Set default to English if available, otherwise use first available
        if not api_keys.get('default') and api_keys.get('en'):
            api_keys['default'] = api_keys['en']
        elif api_keys:
            # Use first available key as default
            first_key = list(api_keys.keys())[0]
            api_keys['default'] = api_keys[first_key]
        
        if api_keys:
            config['api_keys'] = api_keys
            # Log available keys (masked for security)
            masked_keys = {k: f"{v[:4]}...{v[-4:]}" if v else "" for k, v in api_keys.items()}
            print(f"Using global environment API keys: {list(masked_keys.keys())}")
    
    # Update directories if specified in env (optional)
    if os.getenv('INCOMING_AUDIO_DIR'):
        config['directories']['incoming'] = os.getenv('INCOMING_AUDIO_DIR')
    if os.getenv('PROCESSED_AUDIO_DIR'):
        config['directories']['processed'] = os.getenv('PROCESSED_AUDIO_DIR')
    if os.getenv('TRANSCRIPTS_DIR'):
        config['directories']['transcripts'] = os.getenv('TRANSCRIPTS_DIR')
    
    # Update other settings from environment (optional)
    if os.getenv('LOG_LEVEL'):
        config['log_level'] = os.getenv('LOG_LEVEL')
    if os.getenv('DEBUG'):
        config['debug'] = os.getenv('DEBUG').lower() == 'true'
    if os.getenv('MAX_AUDIO_DURATION'):
        config['processing']['max_audio_duration'] = int(os.getenv('MAX_AUDIO_DURATION'))
    if os.getenv('CHUNK_DURATION'):
        config['processing']['chunk_duration'] = int(os.getenv('CHUNK_DURATION'))