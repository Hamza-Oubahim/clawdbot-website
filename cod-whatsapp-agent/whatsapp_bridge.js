// whatsapp_bridge.js - WhatsApp Web.js bridge for Python

const { Client, LocalAuth, MessageMedia } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const express = require('express');
const bodyParser = require('body-parser');

const app = express();
app.use(bodyParser.json());

// WhatsApp Client
const client = new Client({
    authStrategy: new LocalAuth({ dataPath: './wa_session' }),
    puppeteer: {
        headless: true,
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-accelerated-2d-canvas',
            '--no-first-run',
            '--no-zygote',
            '--disable-gpu'
        ]
    }
});

let isReady = false;
let qrCode = null;

// Event handlers
client.on('qr', (qr) => {
    qrCode = qr;
    console.log('📱 QR Code generated! Scan it with WhatsApp:');
    qrcode.generate(qr, { small: true });
});

client.on('ready', () => {
    isReady = true;
    qrCode = null;
    console.log('✅ WhatsApp Client is ready!');
});

client.on('authenticated', () => {
    console.log('🔐 WhatsApp authenticated');
});

client.on('auth_failure', (msg) => {
    console.error('❌ Authentication failed:', msg);
});

client.on('disconnected', (reason) => {
    isReady = false;
    console.log('🔌 WhatsApp disconnected:', reason);
});

// Message handler - forwards to Python backend
client.on('message', async (msg) => {
    // Ignore group messages and status updates
    if (msg.isGroupMsg || msg.isStatus) return;
    
    const contact = await msg.getContact();
    const phone = msg.from.replace('@c.us', '');
    
    console.log(`📩 Message from ${phone}: ${msg.body}`);
    
    // Forward to Python backend
    try {
        const response = await fetch('http://localhost:5000/webhook', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                phone: phone,
                message: msg.body,
                name: contact.pushname || contact.name || phone,
                timestamp: msg.timestamp
            })
        });
        
        const data = await response.json();
        
        if (data.reply) {
            await msg.reply(data.reply);
            console.log(`📤 Reply sent to ${phone}`);
        }
    } catch (error) {
        console.error('Error forwarding message:', error.message);
    }
});

// ============ REST API ============

// Status endpoint
app.get('/status', (req, res) => {
    res.json({
        ready: isReady,
        qr: qrCode
    });
});

// Get QR code
app.get('/qr', (req, res) => {
    if (isReady) {
        res.json({ status: 'connected', qr: null });
    } else if (qrCode) {
        res.json({ status: 'waiting_scan', qr: qrCode });
    } else {
        res.json({ status: 'initializing', qr: null });
    }
});

// Send message endpoint
app.post('/send', async (req, res) => {
    const { phone, message } = req.body;
    
    if (!isReady) {
        return res.status(503).json({ error: 'WhatsApp not connected' });
    }
    
    try {
        const chatId = phone.includes('@c.us') ? phone : `${phone}@c.us`;
        await client.sendMessage(chatId, message);
        res.json({ success: true });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Send image endpoint
app.post('/send-image', async (req, res) => {
    const { phone, imageUrl, caption } = req.body;
    
    if (!isReady) {
        return res.status(503).json({ error: 'WhatsApp not connected' });
    }
    
    try {
        const chatId = phone.includes('@c.us') ? phone : `${phone}@c.us`;
        const media = await MessageMedia.fromUrl(imageUrl);
        await client.sendMessage(chatId, media, { caption });
        res.json({ success: true });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Restart client
app.post('/restart', async (req, res) => {
    try {
        await client.destroy();
        isReady = false;
        client.initialize();
        res.json({ success: true, message: 'Restarting...' });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Start everything
const PORT = process.env.WA_BRIDGE_PORT || 3001;

app.listen(PORT, () => {
    console.log(`🌉 WhatsApp Bridge API running on port ${PORT}`);
});

console.log('🚀 Initializing WhatsApp client...');
client.initialize();
