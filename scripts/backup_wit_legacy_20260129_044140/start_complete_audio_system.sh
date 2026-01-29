#!/bin/bash
# Complete Audio Processing System with Auto-Responder

set -e

echo "========================================"
echo "Starting Complete Audio Processing System"
echo "========================================"

# Set API keys
export WIT_API_KEY_ENGLISH="KZWAXOBLCGWZRFCINDDHRELBSVSI5IUP"
export WIT_API_KEY_ARABIC="FUCGCAM6DSHYHYFEN3HKIHA5ZWB2HFC4"
export WIT_API_KEY_FRENCH="6VRIVMCU2YRRP4PYFHIF2MRRJV3R3BZ7"

echo "API keys set for: English, Arabic, French"

# Check dependencies
echo "Checking dependencies..."
for cmd in python3 ffmpeg ffprobe; do
    if ! command -v $cmd &> /dev/null; then
        echo "ERROR: $cmd is not installed!"
        exit 1
    fi
    echo "✓ $cmd"
done

# Create directories
echo "Creating directories..."
mkdir -p /root/clawd/audio/{incoming,processed,transcripts,processed_sessions}
mkdir -p /root/clawd/{sessions,whatsapp_responses/processed}

# Stop any existing services
echo "Stopping existing services..."
bash /root/clawd/scripts/stop_audio_processing.sh 2>/dev/null || true
pkill -f "audio_auto_responder.py" 2>/dev/null || true
sleep 2

# Start Wit.ai Audio Processor v2
echo "Starting Wit.ai Audio Processor v2..."
cd /root/clawd
nohup python3 scripts/wit_audio_handler_v2.py > /root/clawd/audio/wit_v2.log 2>&1 &
WIT_PID=$!
echo $WIT_PID > /root/clawd/audio/wit_handler.pid
echo "✓ Wit.ai Processor started (PID: $WIT_PID)"

# Start Clawdbot Integration Bridge
echo "Starting Clawdbot Integration Bridge..."
nohup python3 scripts/clawdbot_integration.py --wit-mode > /root/clawd/audio/clawdbot_bridge.log 2>&1 &
BRIDGE_PID=$!
echo $BRIDGE_PID > /root/clawd/audio/clawdbot_bridge.pid
echo "✓ Clawdbot Bridge started (PID: $BRIDGE_PID)"

# Start Auto-Responder
echo "Starting Audio Auto-Responder..."
nohup python3 scripts/audio_auto_responder.py --start > /root/clawd/audio/auto_responder.log 2>&1 &
RESPONDER_PID=$!
echo $RESPONDER_PID > /root/clawd/audio/auto_responder.pid
echo "✓ Auto-Responder started (PID: $RESPONDER_PID)"

echo ""
echo "========================================"
echo "System Started Successfully!"
echo "========================================"
echo ""
echo "Services running:"
echo "  1. Wit.ai Audio Processor v2 (PID: $WIT_PID)"
echo "  2. Clawdbot Integration Bridge (PID: $BRIDGE_PID)"
echo "  3. Audio Auto-Responder (PID: $RESPONDER_PID)"
echo ""
echo "Log files:"
echo "  - /root/clawd/audio/wit_v2.log"
echo "  - /root/clawd/audio/clawdbot_bridge.log"
echo "  - /root/clawd/audio/auto_responder.log"
echo "  - /root/clawd/audio/whatsapp_responses.log"
echo ""
echo "How it works:"
echo "  1. Place audio in: /root/clawd/audio/incoming/"
echo "  2. System detects language (FR/EN/AR)"
echo "  3. Transcribes with correct Wit.ai API"
echo "  4. Creates session file in: /root/clawd/sessions/"
echo "  5. Auto-responder reads session file"
echo "  6. Generates response in same language"
echo "  7. Queues response in: /root/clawd/whatsapp_responses/"
echo ""
echo "To test:"
echo "  python3 scripts/whatsapp_simulator.py --wit"
echo ""
echo "To stop:"
echo "  bash scripts/stop_complete_audio_system.sh"
echo ""
echo "To monitor:"
echo "  tail -f /root/clawd/audio/auto_responder.log"
echo ""

# Create a test response to show it works
echo "Creating test response example..."
cat > /root/clawd/test_response_example.txt << 'EOF'
Example Workflow:
1. French audio: "Salut Sarah, ça va?"
2. Detected as: French
3. Transcript: "Salut Sarah, ça va?"
4. Response: "Bonjour Sarah! Je vais bien, merci de demander. Comment puis-je vous aider aujourd'hui?"
5. Queued for WhatsApp sending

Test with:
cp /path/to/audio.ogg /root/clawd/audio/incoming/212626474248_$(date +%s).ogg
EOF

echo "Test example saved to: /root/clawd/test_response_example.txt"
echo ""
echo "System ready! 🚀"