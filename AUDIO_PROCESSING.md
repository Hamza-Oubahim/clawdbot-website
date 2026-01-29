# Clawdbot Audio Processing Integration

## Overview
This system enables Clawdbot to process WhatsApp voice notes in Moroccan Darija using multiple speech-to-text engines:
1. **OpenAI Whisper API** (default) - High accuracy, paid service
2. **Wit.ai** (Facebook/Meta) - Free tier available, good for multiple languages

## Architecture
```
WhatsApp → Audio File (.ogg) → [Whisper API | Wit.ai] → Text → Clawdbot Session
```

## Components

### 1. Speech-to-Text Handlers
- **`whisper_handler.py`** - OpenAI Whisper API integration
  - Monitors `/root/clawd/audio/incoming/` for new audio files
  - Converts OGG to WAV format using FFmpeg
  - Sends audio to OpenAI Whisper API for transcription
  - Saves transcripts to `/root/clawd/audio/transcripts/`

- **`wit_audio_handler.py`** - Wit.ai integration (NEW)
  - Monitors `/root/clawd/audio/incoming/` for new audio files
  - Supports multiple languages (English, Arabic, French)
  - Automatic language detection from phone number
  - Handles long audio files with chunking
  - Saves transcripts to `/root/clawd/audio/transcripts/`

### 2. `clawdbot_integration.py`
- Monitors transcript directory for new files
- Extracts sender information from filename
- Creates session files for Clawdbot to read
- Injects transcripts into appropriate WhatsApp sessions
- Supports both Whisper and Wit.ai modes

### 3. `whatsapp_simulator.py`
- Simulates WhatsApp webhook payloads
- Creates test audio files
- Supports testing both Whisper and Wit.ai modes
- Useful for development and testing

## Setup Instructions

### Option A: Using OpenAI Whisper API
#### 1. Install Dependencies
```bash
# Run the startup script
bash /root/clawd/scripts/start_audio_processing.sh
```

#### 2. Configure OpenAI API Key
```bash
export OPENAI_API_KEY="sk-your-openai-api-key"
# Or add to Clawdbot config in /root/.clawdbot/clawdbot.json
```

#### 3. Start Services
```bash
# Start Whisper handler (background)
python3 /root/clawd/scripts/whisper_handler.py &

# Start Clawdbot bridge (background)
python3 /root/clawd/scripts/clawdbot_integration.py --start &

# Test the system
python3 /root/clawd/scripts/whatsapp_simulator.py
```

### Option B: Using Wit.ai (Recommended for Free Tier)
#### 1. Get Wit.ai API Key
1. Go to https://wit.ai
2. Create an account or log in
3. Create a new app
4. Go to Settings → API Details
5. Copy your Server Access Token

#### 2. Set Environment Variables
```bash
# Required: Default API key
export WIT_API_KEY_DEFAULT="your_wit_ai_server_access_token"

# Optional: Language-specific keys
export WIT_API_KEY_ENGLISH="english_app_token"
export WIT_API_KEY_ARABIC="arabic_app_token"
export WIT_API_KEY_FRENCH="french_app_token"
```

#### 3. Start Wit.ai Services
```bash
# Start the complete Wit.ai audio processing system
bash /root/clawd/scripts/start_wit_audio_processing.sh

# Test the system
python3 /root/clawd/scripts/whatsapp_simulator.py --wit
```

#### 4. Stop Services
```bash
bash /root/clawd/scripts/stop_audio_processing.sh
```

## Integration with Actual WhatsApp

### Option A: WhatsApp Business API
1. Set up WhatsApp Business API in Meta Developer Portal
2. Configure webhook to point to your server
3. Modify `whisper_handler.py` to handle real webhook payloads
4. Implement media download from WhatsApp servers

### Option B: Direct Gateway Integration
1. Modify Clawdbot's WhatsApp plugin to save audio files
2. Save files to `/root/clawd/audio/incoming/` with naming convention: `PHONE_NUMBER_TIMESTAMP.ogg`
3. System will auto-process them

## File Naming Convention
- Incoming audio: `212635278125_1706476800.ogg`
  - `212635278125` = Sender phone number
  - `1706476800` = Unix timestamp
- Transcript: `212635278125_1706476800.txt`
- Metadata: `212635278125_1706476800.json`

## Testing

### 1. Manual Test
```bash
# Create a test audio file
echo "DUMMY_AUDIO" > /root/clawd/audio/incoming/212635278125_$(date +%s).ogg

# Check processing
tail -f /root/clawd/audio/whisper.log
```

### 2. Automated Test
```bash
python3 /root/clawd/scripts/whatsapp_simulator.py
```

## Monitoring
- Logs: `/root/clawd/audio/whisper.log`
- Processed files: `/root/clawd/audio/processed/`
- Transcripts: `/root/clawd/audio/transcripts/`
- Session files: `/root/clawd/sessions/`

## Performance Notes

### OpenAI Whisper API
- Accuracy: ~70-80% for Moroccan Darija
- Speed: ~2-5 seconds per audio file
- Max file size: 25MB
- Cost: Paid service (per minute of audio)
- Supported formats: OGG, MP3, WAV, M4A, FLAC

### Wit.ai
- Accuracy: ~60-70% for Moroccan Darija (good for English/Arabic/French)
- Speed: ~3-7 seconds per audio file
- Max file size: 20MB (free tier limit)
- Cost: Free tier available (limited requests)
- Supported formats: WAV (16kHz mono recommended)
- Features: Automatic language detection, word-level timing

## Troubleshooting

### Common Issues

1. **No OpenAI API Key**
   ```
   Error: OPENAI_API_KEY environment variable not set
   ```
   Solution: Set the environment variable or update config

2. **FFmpeg not installed**
   ```
   Error: ffmpeg command not found
   ```
   Solution: `apt install ffmpeg`

3. **File permission errors**
   ```
   Permission denied: /root/clawd/audio/incoming/
   ```
   Solution: `chmod -R 755 /root/clawd/audio`

4. **Whisper API errors**
   ```
   Error: Invalid audio file
   ```
   Solution: Ensure audio is in supported format (OGG with Opus codec)

## Next Steps

### Short-term
1. Test with real Darija audio samples
2. Optimize for Moroccan dialect
3. Add error handling and retries

### Long-term
1. Train custom Whisper model for Darija
2. Implement local Whisper.cpp for cost savings
3. Add support for other STT engines (Google, Azure)
4. Real-time streaming transcription

## Security Considerations
1. API keys stored in environment variables
2. Audio files automatically cleaned up after processing
3. No persistent storage of sensitive audio data
4. Rate limiting for API calls

## Support
For issues, check logs and ensure all dependencies are installed.
Test with the simulator before integrating with production WhatsApp.