#!/bin/bash
# start.sh - Start the COD WhatsApp Agent

echo "🚀 Starting COD WhatsApp Agent..."

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing Node.js dependencies..."
    npm install
fi

# Check Python venv
if [ ! -d "venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate venv and install deps
source venv/bin/activate
pip install -r requirements.txt -q

# Start WhatsApp Bridge in background
echo "🌉 Starting WhatsApp Bridge..."
node whatsapp_bridge.js &
WA_PID=$!

# Wait for bridge to be ready
sleep 5

# Start Python backend
echo "🐍 Starting Python Backend..."
python main.py &
PY_PID=$!

echo ""
echo "✅ COD WhatsApp Agent is running!"
echo "   - WhatsApp Bridge: http://localhost:3001"
echo "   - Python Backend:  http://localhost:5000"
echo ""
echo "📱 Check QR Code: curl http://localhost:3001/qr"
echo ""
echo "Press Ctrl+C to stop..."

# Handle shutdown
trap "kill $WA_PID $PY_PID 2>/dev/null; exit" SIGINT SIGTERM

wait
