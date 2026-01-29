# COD WhatsApp Agent 🛒📱

Agent dial Cash on Delivery l WhatsApp. Kat hder Darija/French w kadir tbii3 produits, tjme3 commandes w tsauvgardhom f MySQL.

## Stack

- **WhatsApp**: whatsapp-web.js (Node.js)
- **AI**: Google Gemini
- **Backend**: Python Flask
- **Database**: MySQL

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────┐
│  WhatsApp Web   │◄───►│  Node.js Bridge  │◄───►│   Python    │
│   (Browser)     │     │   (port 3001)    │     │   Backend   │
└─────────────────┘     └──────────────────┘     │  (port 5000)│
                                                  └──────┬──────┘
                                                         │
                              ┌──────────────────────────┼──────────────────────────┐
                              │                          │                          │
                              ▼                          ▼                          ▼
                       ┌─────────────┐           ┌─────────────┐           ┌─────────────┐
                       │   Gemini    │           │    MySQL    │           │ Conversation│
                       │     AI      │           │   Database  │           │   Manager   │
                       └─────────────┘           └─────────────┘           └─────────────┘
```

## Setup

### 1. Prerequisites

```bash
# Node.js 18+
node --version

# Python 3.10+
python3 --version
```

### 2. Configuration

Edit `config.py`:

```python
# Add your Gemini API key
GEMINI_API_KEY = "your-api-key-here"

# Database is already configured
```

### 3. Install Dependencies

```bash
# Node.js
npm install

# Python
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

### 4. Run

```bash
# Option 1: Use start script
chmod +x start.sh
./start.sh

# Option 2: Manual
# Terminal 1 - WhatsApp Bridge
node whatsapp_bridge.js

# Terminal 2 - Python Backend
source venv/bin/activate
python main.py
```

### 5. Connect WhatsApp

1. Open http://localhost:3001/qr
2. Scan QR code with WhatsApp (Link Device)
3. Ready! 🎉

## API Endpoints

### WhatsApp Bridge (port 3001)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/status` | GET | Connection status |
| `/qr` | GET | Get QR code |
| `/send` | POST | Send message |
| `/send-image` | POST | Send image |

### Python Backend (port 5000)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/webhook` | POST | Receive WhatsApp messages |
| `/products` | GET | List products |
| `/categories` | GET | List categories |
| `/orders` | GET | List orders |
| `/sessions` | GET | Active conversations |
| `/test-ai` | POST | Test AI without WhatsApp |

## Testing

```bash
# Test AI response directly
curl -X POST http://localhost:5000/test-ai \
  -H "Content-Type: application/json" \
  -d '{"phone": "+212600000000", "message": "Salam, chnou 3andkom?"}'
```

## Conversation Flow

```
Customer: Salam
Agent: Merhba! Ana agent dial Demo Store Maroc. Kifash n9der n3awnek lyoum?

Customer: Chnou 3andkom?
Agent: 3andna bzaf dyal produits! [Shows categories/products]

Customer: Bghit montre connectée
Agent: [Shows smartwatch details + price] Bghiti tzidha l cart?

Customer: Oui
Agent: ✅ Tzadat! Bghiti tkemmel commande ola tzid chi haja?

Customer: Safi, bghit ncommandi
Agent: Wakha! 3tini smiytek...
Agent: W adresse dial livraison...
Agent: W mdina...

Agent: [Shows order summary] Confirmi b "OUI"?

Customer: Oui
Agent: ✅ Commande confirmée! Merci! 🎉
```

## Files

```
cod-whatsapp-agent/
├── config.py              # Configuration
├── database.py            # MySQL operations
├── ai_agent.py            # Gemini AI agent
├── conversation_manager.py # Session state
├── main.py                # Python Flask backend
├── whatsapp_bridge.js     # Node.js WhatsApp bridge
├── package.json           # Node dependencies
├── requirements.txt       # Python dependencies
├── start.sh              # Start script
└── README.md             # This file
```

## Environment Variables

```bash
export GEMINI_API_KEY="your-key"
export WA_BRIDGE_PORT=3001  # Optional
```

## Production Deployment

For VPS deployment:

```bash
# Use PM2 for process management
npm install -g pm2

# Start WhatsApp Bridge
pm2 start whatsapp_bridge.js --name wa-bridge

# Start Python Backend
pm2 start main.py --interpreter python3 --name cod-backend

# Save and enable startup
pm2 save
pm2 startup
```

## Notes

- WhatsApp Web session is saved in `./wa_session/`
- If disconnected, delete `wa_session/` and re-scan QR
- Messages are processed in real-time
- Orders are saved to MySQL automatically

---

Built with ❤️ for Demo Store Maroc
