#!/bin/bash
# Stop Audio Processing System

echo "Stopping Audio Processing System..."

# Stop Wit.ai handler
if [ -f /root/clawd/audio/wit_handler.pid ]; then
    WIT_PID=$(cat /root/clawd/audio/wit_handler.pid)
    if kill -0 $WIT_PID 2>/dev/null; then
        echo "Stopping Wit.ai handler (PID: $WIT_PID)..."
        kill $WIT_PID
        sleep 2
        if kill -0 $WIT_PID 2>/dev/null; then
            echo "Force killing Wit.ai handler..."
            kill -9 $WIT_PID
        fi
    fi
    rm -f /root/clawd/audio/wit_handler.pid
fi

# Stop Clawdbot bridge
if [ -f /root/clawd/audio/clawdbot_bridge.pid ]; then
    BRIDGE_PID=$(cat /root/clawd/audio/clawdbot_bridge.pid)
    if kill -0 $BRIDGE_PID 2>/dev/null; then
        echo "Stopping Clawdbot bridge (PID: $BRIDGE_PID)..."
        kill $BRIDGE_PID
        sleep 2
        if kill -0 $BRIDGE_PID 2>/dev/null; then
            echo "Force killing Clawdbot bridge..."
            kill -9 $BRIDGE_PID
        fi
    fi
    rm -f /root/clawd/audio/clawdbot_bridge.pid
fi

# Stop any remaining processes
echo "Cleaning up any remaining processes..."
pkill -f "wit_audio_handler.py" || true
pkill -f "clawdbot_integration.py" || true
pkill -f "whisper_handler.py" || true

echo "Audio Processing System stopped."