#!/bin/bash
# Stop Complete Audio Processing System

echo "Stopping Complete Audio Processing System..."

# Stop Auto-Responder
if [ -f /root/clawd/audio/auto_responder.pid ]; then
    RESPONDER_PID=$(cat /root/clawd/audio/auto_responder.pid)
    if kill -0 $RESPONDER_PID 2>/dev/null; then
        echo "Stopping Auto-Responder (PID: $RESPONDER_PID)..."
        kill $RESPONDER_PID
        sleep 2
        if kill -0 $RESPONDER_PID 2>/dev/null; then
            echo "Force killing Auto-Responder..."
            kill -9 $RESPONDER_PID
        fi
    fi
    rm -f /root/clawd/audio/auto_responder.pid
fi

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
pkill -f "wit_audio_handler_v2.py" || true
pkill -f "clawdbot_integration.py" || true
pkill -f "audio_auto_responder.py" || true
pkill -f "wit_audio_handler.py" || true

echo "Complete Audio Processing System stopped."