# conversation_manager.py - Manage conversation state for each customer

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json

class ConversationState(Enum):
    NEW = "new"                          # Just started
    BROWSING = "browsing"                # Looking at products/categories
    VIEWING_PRODUCT = "viewing_product"  # Looking at specific product
    CART = "cart"                        # Has items in cart
    COLLECTING_NAME = "collecting_name"  # Asking for name
    COLLECTING_ADDRESS = "collecting_address"  # Asking for address
    COLLECTING_CITY = "collecting_city"  # Asking for city
    COLLECTING_PHONE = "collecting_phone"  # Confirming phone
    CONFIRMING_ORDER = "confirming_order"  # Final confirmation
    ORDER_COMPLETE = "order_complete"    # Order placed

@dataclass
class CartItem:
    product_id: str
    name: str
    price: float
    quantity: int = 1
    color: Optional[str] = None

@dataclass
class CustomerSession:
    phone: str
    state: ConversationState = ConversationState.NEW
    cart: List[CartItem] = field(default_factory=list)
    customer_name: Optional[str] = None
    customer_address: Optional[str] = None
    customer_city: Optional[str] = None
    last_viewed_product: Optional[str] = None
    last_activity: datetime = field(default_factory=datetime.now)
    message_history: List[Dict] = field(default_factory=list)
    
    def add_to_cart(self, product_id: str, name: str, price: float, quantity: int = 1, color: str = None):
        # Check if already in cart
        for item in self.cart:
            if item.product_id == product_id and item.color == color:
                item.quantity += quantity
                return
        self.cart.append(CartItem(product_id, name, price, quantity, color))
    
    def remove_from_cart(self, product_id: str):
        self.cart = [item for item in self.cart if item.product_id != product_id]
    
    def clear_cart(self):
        self.cart = []
    
    def get_cart_total(self) -> float:
        return sum(item.price * item.quantity for item in self.cart)
    
    def get_cart_summary(self) -> str:
        if not self.cart:
            return "Cart khawi (empty)"
        
        lines = []
        for i, item in enumerate(self.cart, 1):
            color_str = f" ({item.color})" if item.color else ""
            lines.append(f"{i}. {item.name}{color_str} x{item.quantity} = {item.price * item.quantity} DH")
        
        lines.append(f"\n💰 Total: {self.get_cart_total()} DH")
        return "\n".join(lines)
    
    def add_message(self, role: str, content: str):
        self.message_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        # Keep last 20 messages for context
        if len(self.message_history) > 20:
            self.message_history = self.message_history[-20:]
    
    def to_dict(self) -> Dict:
        return {
            "phone": self.phone,
            "state": self.state.value,
            "cart": [{"product_id": i.product_id, "name": i.name, "price": i.price, 
                     "quantity": i.quantity, "color": i.color} for i in self.cart],
            "customer_name": self.customer_name,
            "customer_address": self.customer_address,
            "customer_city": self.customer_city,
            "last_viewed_product": self.last_viewed_product,
            "last_activity": self.last_activity.isoformat()
        }


class ConversationManager:
    def __init__(self):
        self.sessions: Dict[str, CustomerSession] = {}
    
    def get_session(self, phone: str) -> CustomerSession:
        """Get or create a session for a phone number"""
        if phone not in self.sessions:
            self.sessions[phone] = CustomerSession(phone=phone)
        
        session = self.sessions[phone]
        session.last_activity = datetime.now()
        return session
    
    def clear_session(self, phone: str):
        """Clear a session after order completion or timeout"""
        if phone in self.sessions:
            del self.sessions[phone]
    
    def get_context_for_ai(self, phone: str) -> Dict[str, Any]:
        """Get conversation context to send to AI"""
        session = self.get_session(phone)
        return {
            "state": session.state.value,
            "cart": session.get_cart_summary(),
            "cart_total": session.get_cart_total(),
            "cart_items": len(session.cart),
            "customer_name": session.customer_name,
            "customer_address": session.customer_address,
            "customer_city": session.customer_city,
            "last_viewed_product": session.last_viewed_product,
            "message_history": session.message_history[-10:]  # Last 10 messages
        }


# Singleton instance
conversation_manager = ConversationManager()
