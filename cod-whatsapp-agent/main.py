# main.py - Main Python Backend for COD WhatsApp Agent

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import asyncio
import logging
import requests
import os
import json
from datetime import datetime

from config import config
from ai_agent import agent
from database import db
from conversation_manager import conversation_manager

# Get the directory where main.py is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ADMIN_DIR = os.path.join(BASE_DIR, 'admin')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='admin', static_url_path='')
CORS(app)

# WhatsApp Bridge URL
WA_BRIDGE_URL = "http://localhost:3001"


# ==================== ADMIN DASHBOARD ====================

@app.route('/')
def admin_index():
    """Serve admin dashboard"""
    return send_from_directory(ADMIN_DIR, 'index.html')

@app.route('/<path:path>')
def admin_static(path):
    """Serve static files"""
    return send_from_directory(ADMIN_DIR, path)


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "store": config.STORE_NAME
    })


@app.route('/webhook', methods=['POST'])
def webhook():
    """Receive messages from WhatsApp Bridge"""
    try:
        data = request.json
        phone = data.get('phone')
        message = data.get('message', '').strip()
        name = data.get('name', '')
        
        if not phone or not message:
            return jsonify({"error": "Missing phone or message"}), 400
        
        logger.info(f"📩 Received from {phone} ({name}): {message}")
        
        # Process with AI agent
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        reply = loop.run_until_complete(agent.process_message(phone, message))
        loop.close()
        
        logger.info(f"📤 Reply to {phone}: {reply[:100]}...")
        
        return jsonify({"reply": reply})
    
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return jsonify({
            "error": str(e),
            "reply": "⚠️ Smeh liya, kayn mouchkil technique. 3awed men ba3d!"
        }), 500


@app.route('/send', methods=['POST'])
def send_message():
    """Send a message to a phone number"""
    try:
        data = request.json
        phone = data.get('phone')
        message = data.get('message')
        
        if not phone or not message:
            return jsonify({"error": "Missing phone or message"}), 400
        
        # Forward to WhatsApp Bridge
        response = requests.post(
            f"{WA_BRIDGE_URL}/send",
            json={"phone": phone, "message": message}
        )
        
        return jsonify(response.json())
    
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/wa-status', methods=['GET'])
def wa_status():
    """Get WhatsApp connection status"""
    try:
        response = requests.get(f"{WA_BRIDGE_URL}/status", timeout=5)
        return jsonify(response.json())
    except:
        return jsonify({"ready": False, "error": "Bridge not running"})


@app.route('/products', methods=['GET'])
def get_products():
    """Get all products"""
    try:
        category = request.args.get('category')
        if category:
            products = db.get_products_by_category(category)
        else:
            products = db.get_all_products()
        return jsonify(products)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/categories', methods=['GET'])
def get_categories():
    """Get all categories"""
    try:
        categories = db.get_categories()
        return jsonify(categories)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/orders', methods=['GET'])
def get_orders():
    """Get recent orders"""
    try:
        # Simple endpoint - you can expand this
        conn = db.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM orders 
            ORDER BY created_at DESC 
            LIMIT 50
        """)
        orders = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(orders)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/sessions', methods=['GET'])
def get_sessions():
    """Get active conversation sessions"""
    try:
        sessions = {
            phone: session.to_dict() 
            for phone, session in conversation_manager.sessions.items()
        }
        return jsonify(sessions)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/test-ai', methods=['POST'])
def test_ai():
    """Test AI response without WhatsApp"""
    try:
        data = request.json
        phone = data.get('phone', '+212600000000')
        message = data.get('message', 'Salam')
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        reply = loop.run_until_complete(agent.process_message(phone, message))
        loop.close()
        
        return jsonify({
            "reply": reply,
            "session": conversation_manager.get_session(phone).to_dict()
        })
    except Exception as e:
        logger.error(f"Error in test-ai: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/config', methods=['GET', 'POST'])
def manage_config():
    """Get or update configuration"""
    config_file = os.path.join(BASE_DIR, 'config.py')
    
    if request.method == 'GET':
        return jsonify({
            "gemini_model": config.GEMINI_MODEL,
            "store_name": config.STORE_NAME,
            "currency": config.CURRENCY,
            "delivery_fee": config.DEFAULT_DELIVERY_FEE,
            "free_threshold": config.FREE_DELIVERY_THRESHOLD,
            "db_host": config.DB_HOST,
            "db_port": config.DB_PORT,
            "db_name": config.DB_NAME
        })
    
    if request.method == 'POST':
        try:
            data = request.json
            
            # Read current config
            with open(config_file, 'r') as f:
                content = f.read()
            
            # Update values
            if 'gemini_api_key' in data and data['gemini_api_key']:
                import re
                content = re.sub(
                    r'GEMINI_API_KEY: str = ["\'].*["\']',
                    f'GEMINI_API_KEY: str = "{data["gemini_api_key"]}"',
                    content
                )
            
            if 'gemini_model' in data:
                import re
                content = re.sub(
                    r'GEMINI_MODEL: str = ["\'].*["\']',
                    f'GEMINI_MODEL: str = "{data["gemini_model"]}"',
                    content
                )
            
            if 'store_name' in data:
                import re
                content = re.sub(
                    r'STORE_NAME: str = ["\'].*["\']',
                    f'STORE_NAME: str = "{data["store_name"]}"',
                    content
                )
            
            if 'delivery_fee' in data:
                import re
                content = re.sub(
                    r'DEFAULT_DELIVERY_FEE: float = [\d.]+',
                    f'DEFAULT_DELIVERY_FEE: float = {data["delivery_fee"]}',
                    content
                )
            
            if 'free_threshold' in data:
                import re
                content = re.sub(
                    r'FREE_DELIVERY_THRESHOLD: float = [\d.]+',
                    f'FREE_DELIVERY_THRESHOLD: float = {data["free_threshold"]}',
                    content
                )
            
            # Write updated config
            with open(config_file, 'w') as f:
                f.write(content)
            
            return jsonify({"success": True, "message": "Configuration saved. Restart required."})
        except Exception as e:
            return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    logger.info(f"🚀 Starting COD WhatsApp Agent for {config.STORE_NAME}")
    logger.info(f"📊 Database: {config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}")
    
    # Test database connection
    try:
        products = db.get_all_products()
        logger.info(f"✅ Database connected - {len(products)} products found")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
