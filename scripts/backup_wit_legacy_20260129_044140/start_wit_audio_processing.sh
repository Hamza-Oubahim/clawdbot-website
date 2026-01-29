#!/bin/bash
# Start Wit.ai Audio Processing System for Clawdbot

set -e

echo "========================================"
echo "Starting Wit.ai Audio Processing System"
echo "========================================"

# Check for required environment variables
echo "Checking environment variables..."

# Set the API keys you provided
export WIT_API_KEY_ENGLISH="KZWAXOBLCGWZRFCINDDHRELBSVSI5IUP"
export WIT_API_KEY_ARABIC="FUCGCAM6DSHYHYFEN3HKIHA5ZWB2HFC4"
export WIT_API_KEY_FRENCH="6VRIVMCU2YRRP4PYFHIF2MRRJV3R3BZ7"

# Check if at least one key is set
REQUIRED_VARS=("WIT_API_KEY_ENGLISH" "WIT_API_KEY_ARABIC" "WIT_API_KEY_FRENCH" "WIT_API_KEY_DEFAULT")
AVAILABLE_VARS=()

for var in "${REQUIRED_VARS[@]}"; do
    if [ -n "${!var}" ]; then
        AVAILABLE_VARS+=("$var")
    fi
done

if [ ${#AVAILABLE_VARS[@]} -eq 0 ]; then
    echo "ERROR: No Wit.ai API keys found!"
    echo ""
    echo "Please set at least one of:"
    echo "  export WIT_API_KEY_ENGLISH='your_english_key'"
    echo "  export WIT_API_KEY_ARABIC='your_arabic_key'"
    echo "  export WIT_API_KEY_FRENCH='your_french_key'"
    echo "  export WIT_API_KEY_DEFAULT='your_default_key'"
    exit 1
fi

echo "Environment variables check passed!"
echo "Available API keys: ${AVAILABLE_VARS[@]}"

# Check for required commands
echo "Checking for required commands..."
for cmd in python3 ffmpeg ffprobe; do
    if ! command -v $cmd &> /dev/null; then
        echo "ERROR: $cmd is not installed!"
        exit 1
    fi
    echo "✓ $cmd"
done

# Check Python dependencies
echo "Checking Python dependencies..."
PYTHON_DEPS=("requests" "watchdog")

for dep in "${PYTHON_DEPS[@]}"; do
    if ! python3 -c "import $dep" 2>/dev/null; then
        echo "Installing $dep..."
        pip3 install $dep
    fi
    echo "✓ $dep"
done

# Create necessary directories
echo "Creating directories..."
mkdir -p /root/clawd/audio/{incoming,processed,transcripts}
mkdir -p /root/clawd/sessions

# Stop any existing audio processing services
echo "Stopping any existing audio processing services..."
pkill -f "whisper_handler.py" || true
pkill -f "clawdbot_integration.py" || true
pkill -f "wit_audio_handler.py" || true

sleep 2

# Start the Wit.ai handler v2
echo "Starting Wit.ai Audio Handler v2..."
cd /root/clawd
nohup python3 scripts/wit_audio_handler_v2.py > /root/clawd/audio/wit_v2.log 2>&1 &
WIT_PID=$!
echo "Wit.ai handler v2 started with PID: $WIT_PID"

# Start the Clawdbot integration bridge
echo "Starting Clawdbot Integration Bridge..."
nohup python3 scripts/clawdbot_integration.py --wit-mode > /root/clawd/audio/clawdbot_bridge.log 2>&1 &
BRIDGE_PID=$!
echo "Clawdbot bridge started with PID: $BRIDGE_PID"

# Save PIDs to file
echo "$WIT_PID" > /root/clawd/audio/wit_handler.pid
echo "$BRIDGE_PID" > /root/clawd/audio/clawdbot_bridge.pid

echo ""
echo "========================================"
echo "Wit.ai Audio Processing System Started!"
echo "========================================"
echo ""
echo "Services running:"
echo "  - Wit.ai Audio Handler (PID: $WIT_PID)"
echo "  - Clawdbot Integration Bridge (PID: $BRIDGE_PID)"
echo ""
echo "Log files:"
echo "  - /root/clawd/audio/wit.log"
echo "  - /root/clawd/audio/clawdbot_bridge.log"
echo ""
echo "To test the system:"
echo "  python3 scripts/whatsapp_simulator.py --wit"
echo ""
echo "To stop the system:"
echo "  bash scripts/stop_audio_processing.sh"
echo ""
echo "To monitor logs:"
echo "  tail -f /root/clawd/audio/wit.log"
echo ""