# ai_agent.py - Gemini-powered COD Agent with Darija/French personality

import google.generativeai as genai
from typing import Dict, List, Optional, Tuple
import json
import re

from config import config
from database import db
from conversation_manager import conversation_manager, ConversationState

# Configure Gemini
genai.configure(api_key=config.GEMINI_API_KEY)

SYSTEM_PROMPT = """Nta agent dial COD (Cash on Delivery) dyal "{store_name}". 
Kat hder b Darija (Moroccan Arabic) mkhalta m3a French. Kon friendly, helpful, w professional.

🎯 MISSION DYALK:
1. Sallem 3la client w chouf chnou baghi
2. Werri produits li 3andna (men database)
3. 3awen client ykhtar
4. Jme3 les informations: smiya, adresse, mdina, telephone
5. Confirmi commande w taman

💬 PERSONALITY:
- Friendly w warm, bhal sa7bek li 3ando hanout
- Professional mais pas trop formal
- Ila ma fhemtich, souwel poliment
- Ila client 3sban, kon 9aleb w helpful

🛒 PRODUITS DISPONIBLES:
{products}

📦 CATEGORIES:
{categories}

💰 LIVRAISON:
- Livraison: {delivery_fee} DH
- Livraison GRATUITE 3la les commandes > {free_delivery_threshold} DH

📋 CURRENT CONVERSATION STATE:
{context}

🔧 RESPONSE FORMAT:
Rje3 JSON object b had structure:
{{
    "message": "رسالتك للclient (Darija/French mix)",
    "action": "none|show_products|show_categories|add_to_cart|remove_from_cart|checkout|collect_info|confirm_order|complete_order",
    "action_data": {{}} // Optional data for the action
}}

ACTIONS:
- "show_products": werri products (action_data: {{"category": "optional category"}})
- "show_categories": werri categories
- "add_to_cart": zid l cart (action_data: {{"product_id": "...", "quantity": 1}})
- "checkout": bda checkout process
- "collect_info": jme3 info (action_data: {{"field": "name|address|city|phone", "value": "..."}})
- "confirm_order": werri summary dyal order bach client y confirmi
- "complete_order": sali order (action_data: {{"confirmed": true}})
- "none": ghir message, bla action

IMPORTANT:
- Toujours rje3 valid JSON
- Ila client gal "oui", "ok", "wah", "d'accord" f confirmation = complete_order
- Ila client baghi ybddel chi haja, 3awdo l browsing
- Ila client gal "safi" ola "khalas" ola "non merci" = complete conversation politely
"""

class CODAgent:
    def __init__(self):
        self.model = genai.GenerativeModel(
            model_name=config.GEMINI_MODEL,
            generation_config={
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 1024,
            }
        )
    
    def get_products_text(self) -> str:
        """Format products for the AI prompt"""
        products = db.get_all_products()
        if not products:
            return "Ma kayn ta produit disponible daba."
        
        lines = []
        for p in products:
            promo = ""
            if p.get('compare_at_price') and p['compare_at_price'] > p['price']:
                promo = f" (كان {p['compare_at_price']} DH - PROMO!)"
            
            colors = ""
            if p.get('colors'):
                colors = f" | Colors: {', '.join(p['colors'])}"
            
            shipping = " 🚚 FREE SHIPPING" if p.get('is_free_shipping') else ""
            
            lines.append(
                f"• [{p['id'][:8]}] {p['name']} - {p['price']} DH{promo}{colors}{shipping}\n"
                f"  📝 {p['description'][:100]}..."
            )
        
        return "\n".join(lines)
    
    def get_categories_text(self) -> str:
        """Format categories for the AI prompt"""
        categories = db.get_categories()
        return ", ".join(categories) if categories else "Ma kayn categories"
    
    def build_prompt(self, phone: str, user_message: str) -> str:
        """Build the full prompt with context"""
        context = conversation_manager.get_context_for_ai(phone)
        
        return SYSTEM_PROMPT.format(
            store_name=config.STORE_NAME,
            products=self.get_products_text(),
            categories=self.get_categories_text(),
            delivery_fee=config.DEFAULT_DELIVERY_FEE,
            free_delivery_threshold=config.FREE_DELIVERY_THRESHOLD,
            context=json.dumps(context, ensure_ascii=False, indent=2)
        )
    
    def parse_response(self, response_text: str) -> Dict:
        """Parse AI response JSON"""
        # Try to extract JSON from response
        try:
            # Find JSON in response
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
        
        # Fallback: return as plain message
        return {
            "message": response_text,
            "action": "none",
            "action_data": {}
        }
    
    def execute_action(self, phone: str, action: str, action_data: Dict) -> Optional[str]:
        """Execute the action and return additional message if needed"""
        session = conversation_manager.get_session(phone)
        
        if action == "show_products":
            category = action_data.get("category")
            if category:
                products = db.get_products_by_category(category)
            else:
                products = db.get_all_products()
            
            if not products:
                return "\n\n❌ Ma l9itch ta produit f had category."
            
            session.state = ConversationState.BROWSING
            return self._format_products_message(products)
        
        elif action == "show_categories":
            categories = db.get_categories()
            session.state = ConversationState.BROWSING
            return "\n\n📂 Categories dyalna:\n" + "\n".join(f"• {c}" for c in categories)
        
        elif action == "add_to_cart":
            product_id = action_data.get("product_id")
            quantity = action_data.get("quantity", 1)
            
            # Find product (could be partial ID)
            products = db.get_all_products()
            product = None
            for p in products:
                if p['id'].startswith(product_id) or product_id in p['name'].lower():
                    product = p
                    break
            
            if product:
                session.add_to_cart(
                    product['id'], 
                    product['name'], 
                    float(product['price']), 
                    quantity
                )
                session.state = ConversationState.CART
                return f"\n\n✅ {product['name']} tzad l cart!\n\n🛒 Cart dyalk:\n{session.get_cart_summary()}"
            else:
                return "\n\n❌ Ma l9itch had produit. Chouf list dial produits."
        
        elif action == "checkout":
            if not session.cart:
                return "\n\n❌ Cart khawi! Khass tzid chi produit 9bel."
            session.state = ConversationState.COLLECTING_NAME
            return None
        
        elif action == "collect_info":
            field = action_data.get("field")
            value = action_data.get("value")
            
            if field == "name" and value:
                session.customer_name = value
                session.state = ConversationState.COLLECTING_ADDRESS
            elif field == "address" and value:
                session.customer_address = value
                session.state = ConversationState.COLLECTING_CITY
            elif field == "city" and value:
                session.customer_city = value
                session.state = ConversationState.CONFIRMING_ORDER
            elif field == "phone" and value:
                # Phone already known from WhatsApp
                session.state = ConversationState.CONFIRMING_ORDER
            
            return None
        
        elif action == "confirm_order":
            session.state = ConversationState.CONFIRMING_ORDER
            return self._format_order_summary(session)
        
        elif action == "complete_order":
            if action_data.get("confirmed"):
                return self._complete_order(session)
            else:
                session.state = ConversationState.BROWSING
                return "\n\n🔄 Ok, ila bghiti tbddel chi haja goul liya!"
        
        return None
    
    def _format_products_message(self, products: List[Dict]) -> str:
        """Format products list for WhatsApp"""
        lines = ["\n\n🛍️ **PRODUITS DISPONIBLES:**\n"]
        
        for i, p in enumerate(products[:10], 1):  # Limit to 10
            promo = ""
            if p.get('compare_at_price') and float(p['compare_at_price']) > float(p['price']):
                promo = f" ~~{p['compare_at_price']}~~ 🔥"
            
            lines.append(f"{i}. *{p['name']}*\n   💰 {p['price']} DH{promo}\n")
        
        lines.append("\n_Goul liya numero ola smiya dyal produit li baghi!_")
        return "\n".join(lines)
    
    def _format_order_summary(self, session) -> str:
        """Format order summary for confirmation"""
        total = session.get_cart_total()
        delivery = 0 if total >= config.FREE_DELIVERY_THRESHOLD else config.DEFAULT_DELIVERY_FEE
        final_total = total + delivery
        
        summary = f"""

📋 **RÉSUMÉ DYAL COMMANDE:**

🛒 **Produits:**
{session.get_cart_summary()}

🚚 **Livraison:** {"GRATUITE! 🎉" if delivery == 0 else f"{delivery} DH"}

💰 **TOTAL FINAL: {final_total} DH**

👤 **Informations:**
• Smiya: {session.customer_name or "❌ Manquant"}
• Adresse: {session.customer_address or "❌ Manquant"}  
• Mdina: {session.customer_city or "❌ Manquant"}
• Téléphone: {session.phone}

_Goul "OUI" bach t confirmi, ola "NON" bach tbddel chi haja._
"""
        return summary
    
    def _complete_order(self, session) -> str:
        """Complete the order and save to database"""
        try:
            # Prepare order data
            products_data = [
                {
                    "product_id": item.product_id,
                    "name": item.name,
                    "price": item.price,
                    "quantity": item.quantity,
                    "color": item.color
                }
                for item in session.cart
            ]
            
            total = session.get_cart_total()
            delivery = 0 if total >= config.FREE_DELIVERY_THRESHOLD else config.DEFAULT_DELIVERY_FEE
            final_total = total + delivery
            
            # Create order in database
            order_id = db.create_order(
                customer_name=session.customer_name,
                customer_phone=session.phone,
                address=session.customer_address,
                city=session.customer_city,
                products=products_data,
                total_price=final_total
            )
            
            # Clear session for next order
            session.state = ConversationState.ORDER_COMPLETE
            session.clear_cart()
            
            return f"""

✅ **COMMANDE CONFIRMÉE!** 🎉

📦 Numéro dyal commande: `{order_id[:8]}`
💰 Total: {final_total} DH (Cash on Delivery)

Ghadi ncontactiw m3ak 9riiiib bach n confirmiw livraison.

Choukran bzaf! 🙏
Ila 3andek chi soual, ana hna!
"""
        except Exception as e:
            return f"\n\n❌ Kayn mouchkil f commande. 3awed men ba3d ola contacti support. ({str(e)[:50]})"
    
    async def process_message(self, phone: str, message: str) -> str:
        """Process incoming message and return response"""
        session = conversation_manager.get_session(phone)
        
        # Add user message to history
        session.add_message("user", message)
        
        # Build prompt with context
        full_prompt = self.build_prompt(phone, message)
        
        # Create conversation with system prompt
        chat = self.model.start_chat(history=[])
        
        # Send the context as system message + user message
        response = chat.send_message(f"{full_prompt}\n\nUser message: {message}")
        
        # Parse response
        parsed = self.parse_response(response.text)
        
        # Execute action if any
        action = parsed.get("action", "none")
        action_data = parsed.get("action_data", {})
        
        additional_message = ""
        if action != "none":
            result = self.execute_action(phone, action, action_data)
            if result:
                additional_message = result
        
        # Combine message
        final_message = parsed.get("message", "") + additional_message
        
        # Add to history
        session.add_message("assistant", final_message)
        
        return final_message


# Singleton instance
agent = CODAgent()
