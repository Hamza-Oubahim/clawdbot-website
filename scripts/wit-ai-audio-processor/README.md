# Wit.ai Audio Processor

Professional audio processing system using Wit.ai speech-to-text API with automatic language detection.

**Uses Global Clawdbot Environment Variables** - No separate configuration needed!

## Features

- **Global Environment Integration**: Uses existing Clawdbot API keys
- **Multi-language Support**: English, Arabic, French with automatic detection
- **Smart Language Detection**: Based on phone numbers (212 = Moroccan Arabic)
- **Audio Format Support**: OGG, MP3, WAV, M4A, FLAC, OPUS
- **Automatic Monitoring**: Watches directory for new audio files
- **Clawdbot Integration**: Creates session files for immediate processing
- **Comprehensive Logging**: Detailed logs for debugging
- **No Separate Config**: Uses global environment variables

## Quick Start

### 1. Check Global Environment
The system uses Clawdbot's global environment variables:
```bash
# Verify your Wit.ai API keys are set globally
env | grep WIT_API_KEY

# Should show:
# WIT_API_KEY_ENGLISH=KZWAXOBLCGWZRFCINDDHRELBSVSI5IUP
# WIT_API_KEY_ARABIC=FUCGCAM6DSHYHYFEN3HKIHA5ZWB2HFC4
# WIT_API_KEY_FRENCH=6VRIVMCU2YRRP4PYFHIF2MRRJV3R3BZ7
```

### 2. Install Dependencies
```bash
cd /root/clawd/scripts/wit-ai-audio-processor

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Install ffmpeg (system dependency)
apt-get update && apt-get install -y ffmpeg
```

### 3. Run the Processor
```bash
# Uses global environment automatically
./run.sh
```

## Global Environment Variables Used

The system automatically uses these Clawdbot global environment variables:

### Required (at least one):
- `WIT_API_KEY_ENGLISH` - English language Wit.ai token
- `WIT_API_KEY_ARABIC` - Arabic language Wit.ai token  
- `WIT_API_KEY_FRENCH` - French language Wit.ai token

### Optional (for reference/logging):
- `OPENAI_API_KEY` - OpenAI API key
- `GEMINI_API_KEY` - Google Gemini API key
- `DEEPSEEK_API_KEY` - DeepSeek API key

## No Configuration Needed!

Unlike the old system, **no separate `.env` file is required**. The system automatically:
1. Reads API keys from global Clawdbot environment
2. Maps them to appropriate languages
3. Uses English as default if available
4. Falls back to first available key

## File Structure

```
wit-ai-audio-processor/
├── src/
│   ├── main.py              # Entry point (uses global env)
│   ├── core/
│   │   ├── wit_handler.py   # Wit.ai processing logic
│   │   └── file_monitor.py  # Directory monitoring
│   └── utils/
│       └── config_loader.py # Global env integration
├── config/
│   └── settings.json        # General settings (no API keys)
├── docs/                    # Documentation
├── logs/                    # Log files (auto-created)
├── requirements.txt         # Python dependencies
├── run.sh                   # Launch script
└── README.md               # This file
```

## How It Works

1. **Global Environment**: Reads API keys from Clawdbot's global environment
2. **File Detection**: Monitors `incoming` directory for new audio files
3. **Language Detection**: Analyzes phone number (212 = Moroccan → Arabic)
4. **Audio Conversion**: Converts to WAV format (16kHz mono)
5. **Wit.ai Processing**: Sends to appropriate Wit.ai API endpoint
6. **Transcript Saving**: Stores JSON with metadata and transcript
7. **Clawdbot Integration**: Creates session file for immediate response
8. **File Management**: Moves processed files to `processed` directory

## Language Detection Logic

1. **Phone number starts with 212** → Arabic (Moroccan Darija)
2. **Other phone numbers** → English (if key available) or Default
3. **No phone number** → Default language (English if available)

## Testing

### Simulate Audio File
```bash
# Create test audio directory
mkdir -p /root/clawd/audio/incoming

# Create test file
cp /path/to/test.ogg /root/clawd/audio/incoming/212626474248_$(date +%s).ogg
```

### Check Logs
```bash
tail -f logs/wit_processor.log
```

### Verify Global Environment
```bash
# Check if system can access global env
cd /root/clawd/scripts/wit-ai-audio-processor
python -c "import os; print('WIT keys:', [k for k in os.environ if 'WIT' in k])"
```

## Integration with Clawdbot

The processor creates session files in `/root/clawd/sessions/` with format:
- Filename: `wit_{phone}_{timestamp}.txt`
- Content: Formatted message with transcript

Clawdbot automatically reads and processes these session files.

## Troubleshooting

### Common Issues

1. **No API Keys in Environment**: 
   ```bash
   # Check what's available
   env | grep API_KEY
   
   # The system needs at least one WIT_API_KEY_* variable
   ```

2. **FFmpeg Missing**: Install with `apt-get install ffmpeg`
3. **Permission Issues**: Check directory permissions
4. **Network Errors**: Verify internet connectivity

### Log Files
- `logs/wit_processor.log` - Main application log
- Check for detailed error messages

### Debug Mode
Set `DEBUG=true` in global environment for verbose logging.

## Maintenance

### Cleanup Old Files
```bash
# Clean processed files older than 30 days
find /root/clawd/audio/processed -type f -mtime +30 -delete

# Clean old session files
find /root/clawd/sessions -name "wit_*.txt" -mtime +7 -delete
```

### Update Dependencies
```bash
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

## Benefits of Global Environment Integration

1. **Single Source of Truth**: API keys managed in one place (Clawdbot)
2. **Security**: No duplicate API keys in multiple files
3. **Simplicity**: No need to maintain separate `.env` files
4. **Consistency**: Same keys used across all Clawdbot components
5. **Easy Updates**: Update keys once in Clawdbot, all projects benefit

## License

Part of Clawdbot ecosystem. See main project for licensing.
