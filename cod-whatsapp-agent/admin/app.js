// API Configuration
const API_BASE = window.location.hostname === 'localhost' 
    ? 'http://localhost:5000'
    : `http://${window.location.hostname}:5000`;

const WA_BRIDGE = window.location.hostname === 'localhost'
    ? 'http://localhost:3001'
    : `http://${window.location.hostname}:3001`;

// State
let logs = [];
let refreshInterval = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    checkStatus();
    startAutoRefresh();
    loadProducts();
});

// Navigation
function initNavigation() {
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const section = item.dataset.section;
            showSection(section);
        });
    });
}

function showSection(sectionId) {
    // Update nav
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.toggle('active', item.dataset.section === sectionId);
    });
    
    // Update sections
    document.querySelectorAll('.section').forEach(section => {
        section.classList.toggle('active', section.id === `section-${sectionId}`);
    });
    
    // Update title
    const titles = {
        dashboard: 'Dashboard',
        whatsapp: 'WhatsApp Connection',
        settings: 'Settings',
        products: 'Products',
        orders: 'Orders',
        conversations: 'Active Conversations',
        logs: 'Logs & Testing'
    };
    document.getElementById('page-title').textContent = titles[sectionId] || 'Dashboard';
    
    // Load section data
    if (sectionId === 'whatsapp') refreshQR();
    if (sectionId === 'products') loadProducts();
    if (sectionId === 'orders') loadOrders();
    if (sectionId === 'conversations') loadSessions();
}

// Status Checking
async function checkStatus() {
    try {
        // Check backend
        const backendRes = await fetch(`${API_BASE}/health`).catch(() => null);
        const backendOk = backendRes && backendRes.ok;
        
        document.getElementById('backend-status').textContent = backendOk ? 'Online' : 'Offline';
        document.getElementById('health-backend').textContent = backendOk ? '● Online' : '● Offline';
        document.getElementById('health-backend').className = `health-status ${backendOk ? 'online' : 'offline'}`;
        
        // Check WhatsApp
        const waRes = await fetch(`${WA_BRIDGE}/status`).catch(() => null);
        let waStatus = 'Offline';
        let waOk = false;
        
        if (waRes && waRes.ok) {
            const waData = await waRes.json();
            waOk = waData.ready;
            waStatus = waData.ready ? 'Connected' : 'Waiting QR';
        }
        
        document.getElementById('wa-status').textContent = waStatus;
        document.getElementById('health-wa').textContent = waOk ? '● Connected' : waStatus === 'Waiting QR' ? '● Waiting' : '● Offline';
        document.getElementById('health-wa').className = `health-status ${waOk ? 'online' : waStatus === 'Waiting QR' ? 'warning' : 'offline'}`;
        
        // Update global status
        const globalStatus = document.getElementById('global-status');
        const statusDot = globalStatus.querySelector('.status-dot');
        
        if (backendOk && waOk) {
            globalStatus.innerHTML = '<span class="status-dot online"></span> All Systems Online';
        } else if (backendOk) {
            globalStatus.innerHTML = '<span class="status-dot"></span> WhatsApp Disconnected';
        } else {
            globalStatus.innerHTML = '<span class="status-dot offline"></span> Backend Offline';
        }
        
        // Check products
        if (backendOk) {
            const productsRes = await fetch(`${API_BASE}/products`);
            const products = await productsRes.json();
            document.getElementById('product-count').textContent = Array.isArray(products) ? products.length : 0;
            document.getElementById('health-db').textContent = '● Connected';
            document.getElementById('health-db').className = 'health-status online';
        }
        
        // Check sessions
        if (backendOk) {
            const sessionsRes = await fetch(`${API_BASE}/sessions`);
            const sessions = await sessionsRes.json();
            document.getElementById('session-count').textContent = Object.keys(sessions).length;
        }
        
        // Check Gemini (we'll assume it's configured if backend is up)
        document.getElementById('health-gemini').textContent = '● Check Required';
        document.getElementById('health-gemini').className = 'health-status warning';
        
    } catch (error) {
        console.error('Status check failed:', error);
    }
}

function startAutoRefresh() {
    if (refreshInterval) clearInterval(refreshInterval);
    refreshInterval = setInterval(checkStatus, 10000);
}

// QR Code
async function refreshQR() {
    const qrStatus = document.getElementById('qr-status');
    const qrCode = document.getElementById('qr-code');
    
    try {
        const res = await fetch(`${WA_BRIDGE}/qr`);
        const data = await res.json();
        
        if (data.status === 'connected') {
            qrStatus.textContent = '✅ WhatsApp Connected!';
            qrStatus.className = 'qr-status connected';
            qrCode.innerHTML = '<p style="color: #22c55e; font-size: 48px;">✓</p>';
        } else if (data.status === 'waiting_scan' && data.qr) {
            qrStatus.textContent = '📱 Scan this QR code with WhatsApp';
            qrStatus.className = 'qr-status waiting';
            
            // Generate QR code using a library
            qrCode.innerHTML = '';
            if (typeof QRCode !== 'undefined') {
                new QRCode(qrCode, {
                    text: data.qr,
                    width: 256,
                    height: 256,
                    colorDark: '#000000',
                    colorLight: '#ffffff'
                });
            } else {
                // Fallback: Show QR data link to external generator
                qrCode.innerHTML = `
                    <img src="https://api.qrserver.com/v1/create-qr-code/?size=256x256&data=${encodeURIComponent(data.qr)}" 
                         alt="QR Code" width="256" height="256">
                `;
            }
        } else {
            qrStatus.textContent = '⏳ Initializing WhatsApp...';
            qrStatus.className = 'qr-status';
            qrCode.innerHTML = '<p>Please wait...</p>';
        }
    } catch (error) {
        qrStatus.textContent = '❌ WhatsApp Bridge Offline';
        qrStatus.className = 'qr-status';
        qrCode.innerHTML = '<p>Start the WhatsApp bridge first</p>';
    }
}

// Products
async function loadProducts() {
    const tbody = document.getElementById('products-body');
    tbody.innerHTML = '<tr><td colspan="5" class="loading">Loading...</td></tr>';
    
    try {
        const res = await fetch(`${API_BASE}/products`);
        const products = await res.json();
        
        if (!Array.isArray(products) || products.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="loading">No products found</td></tr>';
            return;
        }
        
        tbody.innerHTML = products.map(p => {
            const images = p.images || [];
            const imageUrl = images[0] || 'https://via.placeholder.com/48';
            return `
                <tr>
                    <td><img src="${imageUrl}" alt="${p.name}"></td>
                    <td><strong>${p.name}</strong></td>
                    <td>${p.category || '-'}</td>
                    <td>${p.price} DH</td>
                    <td>${p.stock}</td>
                </tr>
            `;
        }).join('');
    } catch (error) {
        tbody.innerHTML = '<tr><td colspan="5" class="loading">Failed to load products</td></tr>';
    }
}

// Orders
async function loadOrders() {
    const tbody = document.getElementById('orders-body');
    tbody.innerHTML = '<tr><td colspan="6" class="loading">Loading...</td></tr>';
    
    try {
        const res = await fetch(`${API_BASE}/orders`);
        const orders = await res.json();
        
        if (!Array.isArray(orders) || orders.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="loading">No orders yet</td></tr>';
            return;
        }
        
        tbody.innerHTML = orders.map(o => `
            <tr>
                <td><code>${(o.id || '').substring(0, 8)}</code></td>
                <td>${o.customer_name || '-'}</td>
                <td>${o.customer_phone || '-'}</td>
                <td><strong>${o.total_price} DH</strong></td>
                <td><span class="session-state">${o.status || 'pending'}</span></td>
                <td>${new Date(o.created_at).toLocaleDateString()}</td>
            </tr>
        `).join('');
    } catch (error) {
        tbody.innerHTML = '<tr><td colspan="6" class="loading">Failed to load orders</td></tr>';
    }
}

// Sessions
async function loadSessions() {
    const container = document.getElementById('sessions-container');
    container.innerHTML = '<p class="loading">Loading...</p>';
    
    try {
        const res = await fetch(`${API_BASE}/sessions`);
        const sessions = await res.json();
        
        const sessionKeys = Object.keys(sessions);
        if (sessionKeys.length === 0) {
            container.innerHTML = '<p class="loading">No active conversations</p>';
            return;
        }
        
        container.innerHTML = sessionKeys.map(phone => {
            const s = sessions[phone];
            return `
                <div class="session-card">
                    <div class="session-header">
                        <span class="session-phone">📱 ${phone}</span>
                        <span class="session-state">${s.state}</span>
                    </div>
                    <div class="session-cart">
                        ${s.cart_items > 0 ? `🛒 ${s.cart_items} items in cart` : 'Empty cart'}
                    </div>
                    ${s.customer_name ? `<div class="session-cart">👤 ${s.customer_name}</div>` : ''}
                </div>
            `;
        }).join('');
    } catch (error) {
        container.innerHTML = '<p class="loading">Failed to load sessions</p>';
    }
}

// Test AI
async function testAI() {
    const message = document.getElementById('ai-test-message').value;
    const responseDiv = document.getElementById('ai-response');
    
    if (!message) {
        showToast('Please enter a message', 'warning');
        return;
    }
    
    responseDiv.textContent = 'Thinking...';
    responseDiv.classList.add('show');
    
    try {
        const res = await fetch(`${API_BASE}/test-ai`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone: '+212600000000', message })
        });
        
        const data = await res.json();
        
        if (data.error) {
            responseDiv.textContent = `❌ Error: ${data.error}`;
        } else {
            responseDiv.textContent = `🤖 AI Response:\n\n${data.reply}`;
        }
    } catch (error) {
        responseDiv.textContent = `❌ Error: ${error.message}`;
    }
}

// Send Test Message
async function sendTestMessage() {
    const phone = document.getElementById('test-phone').value;
    const message = document.getElementById('test-message').value;
    
    if (!phone || !message) {
        showToast('Please enter phone and message', 'warning');
        return;
    }
    
    try {
        const res = await fetch(`${WA_BRIDGE}/send`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone, message })
        });
        
        const data = await res.json();
        
        if (data.success) {
            showToast('Message sent!', 'success');
        } else {
            showToast(`Failed: ${data.error}`, 'error');
        }
    } catch (error) {
        showToast(`Error: ${error.message}`, 'error');
    }
}

// Save API Config
async function saveApiConfig() {
    const apiKey = document.getElementById('gemini-key').value;
    const model = document.getElementById('gemini-model').value;
    
    if (!apiKey) {
        showToast('Please enter your Gemini API key', 'warning');
        return;
    }
    
    try {
        const res = await fetch(`${API_BASE}/config`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ gemini_api_key: apiKey, gemini_model: model })
        });
        
        if (res.ok) {
            showToast('Configuration saved!', 'success');
        } else {
            showToast('Failed to save configuration', 'error');
        }
    } catch (error) {
        showToast(`Error: ${error.message}`, 'error');
    }
}

// Save Store Config
async function saveStoreConfig() {
    const config = {
        store_name: document.getElementById('store-name').value,
        currency: document.getElementById('currency').value,
        delivery_fee: document.getElementById('delivery-fee').value,
        free_threshold: document.getElementById('free-threshold').value
    };
    
    try {
        const res = await fetch(`${API_BASE}/config`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
        });
        
        if (res.ok) {
            showToast('Store settings saved!', 'success');
        } else {
            showToast('Failed to save settings', 'error');
        }
    } catch (error) {
        showToast(`Error: ${error.message}`, 'error');
    }
}

// Test DB Connection
async function testDbConnection() {
    try {
        const res = await fetch(`${API_BASE}/products`);
        if (res.ok) {
            showToast('Database connection successful!', 'success');
        } else {
            showToast('Database connection failed', 'error');
        }
    } catch (error) {
        showToast(`Connection error: ${error.message}`, 'error');
    }
}

// Restart Services
async function restartServices() {
    showToast('Restarting services...', 'warning');
    
    try {
        await fetch(`${WA_BRIDGE}/restart`, { method: 'POST' });
        showToast('Services restarting...', 'success');
        setTimeout(checkStatus, 5000);
    } catch (error) {
        showToast('Restart command sent', 'warning');
    }
}

// Logs
function refreshLogs() {
    const logOutput = document.getElementById('log-output');
    logOutput.textContent = logs.join('\n') || 'No logs yet...';
}

function clearLogs() {
    logs = [];
    document.getElementById('log-output').textContent = 'Logs cleared.';
}

function addLog(message) {
    const timestamp = new Date().toLocaleTimeString();
    logs.push(`[${timestamp}] ${message}`);
    if (logs.length > 500) logs.shift();
}

// Utilities
function togglePassword(inputId) {
    const input = document.getElementById(inputId);
    input.type = input.type === 'password' ? 'text' : 'password';
}

function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// Poll for status updates
setInterval(() => {
    const section = document.querySelector('.section.active');
    if (section && section.id === 'section-whatsapp') {
        refreshQR();
    }
}, 5000);
