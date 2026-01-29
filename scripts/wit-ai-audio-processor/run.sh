#!/bin/bash

# Wit.ai Audio Processor Runner
# Uses global Clawdbot environment variables

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================"
echo "Wit.ai Audio Processor v2.0"
echo "Using Global Clawdbot Environment"
echo "========================================"

# Check for required commands
command -v python3 >/dev/null 2>&1 || { echo "Python3 not found. Please install python3."; exit 1; }
command -v ffmpeg >/dev/null 2>&1 || { echo "FFmpeg not found. Please install ffmpeg."; exit 1; }

# Activate Python virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating Python virtual environment..."
    source venv/bin/activate
else
    echo "Warning: Virtual environment not found."
    echo "Create with: python -m venv venv"
    echo "Continue without virtual environment? (y/n)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check for global environment variables
echo "Checking global Clawdbot environment..."
WIT_KEYS_FOUND=0

if [ -n "$WIT_API_KEY_ENGLISH" ]; then
    echo "  ✓ WIT_API_KEY_ENGLISH: Present"
    WIT_KEYS_FOUND=$((WIT_KEYS_FOUND + 1))
else
    echo "  ✗ WIT_API_KEY_ENGLISH: Not set"
fi

if [ -n "$WIT_API_KEY_ARABIC" ]; then
    echo "  ✓ WIT_API_KEY_ARABIC: Present"
    WIT_KEYS_FOUND=$((WIT_KEYS_FOUND + 1))
else
    echo "  ✗ WIT_API_KEY_ARABIC: Not set"
fi

if [ -n "$WIT_API_KEY_FRENCH" ]; then
    echo "  ✓ WIT_API_KEY_FRENCH: Present"
    WIT_KEYS_FOUND=$((WIT_KEYS_FOUND + 1))
else
    echo "  ✗ WIT_API_KEY_FRENCH: Not set"
fi

# Check other global API keys (for reference)
echo ""
echo "Other global API keys available:"
if [ -n "$OPENAI_API_KEY" ]; then
    masked_openai="${OPENAI_API_KEY:0:4}...${OPENAI_API_KEY: -4}"
    echo "  ✓ OPENAI_API_KEY: $masked_openai"
else
    echo "  ✗ OPENAI_API_KEY: Not set"
fi

if [ -n "$GEMINI_API_KEY" ]; then
    masked_gemini="${GEMINI_API_KEY:0:4}...${GEMINI_API_KEY: -4}"
    echo "  ✓ GEMINI_API_KEY: $masked_gemini"
else
    echo "  ✗ GEMINI_API_KEY: Not set"
fi

if [ -n "$DEEPSEEK_API_KEY" ]; then
    masked_deepseek="${DEEPSEEK_API_KEY:0:4}...${DEEPSEEK_API_KEY: -4}"
    echo "  ✓ DEEPSEEK_API_KEY: $masked_deepseek"
else
    echo "  ✗ DEEPSEEK_API_KEY: Not set"
fi

if [ $WIT_KEYS_FOUND -eq 0 ]; then
    echo ""
    echo "ERROR: No Wit.ai API keys found in global environment!"
    echo ""
    echo "The following Wit.ai keys should be set in Clawdbot's global environment:"
    echo "  - WIT_API_KEY_ENGLISH"
    echo "  - WIT_API_KEY_ARABIC" 
    echo "  - WIT_API_KEY_FRENCH"
    echo ""
    echo "At least one Wit.ai API key is required."
    exit 1
fi

echo ""
echo "Found $WIT_KEYS_FOUND Wit.ai API key(s) in global environment."

# Create required directories
echo "Creating directories..."
mkdir -p logs
mkdir -p /root/clawd/audio/incoming
mkdir -p /root/clawd/audio/processed
mkdir -p /root/clawd/audio/transcripts
mkdir -p /root/clawd/sessions

# Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "Checking Python dependencies..."
    pip install -q -r requirements.txt
fi

echo ""
echo "Starting Wit.ai Audio Processor..."
echo "Using global Clawdbot environment variables"
echo "Monitoring: /root/clawd/audio/incoming"
echo "Log file: logs/wit_processor.log"
echo "Press Ctrl+C to stop"
echo "========================================"

# Run the main processor
python src/main.py "$@"