# database.py - MySQL Database Operations

import mysql.connector
from mysql.connector import pooling
from typing import Optional, List, Dict, Any
from config import config
import json
import uuid
from datetime import datetime

class Database:
    def __init__(self):
        self.pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name="cod_pool",
            pool_size=5,
            host=config.DB_HOST,
            port=config.DB_PORT,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=config.DB_NAME
        )
    
    def get_connection(self):
        return self.pool.get_connection()
    
    # ==================== PRODUCTS ====================
    
    def get_all_products(self, status: str = "active") -> List[Dict]:
        """Get all active products"""
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT id, name, price, compare_at_price, description, 
                       images, category, stock, is_free_shipping, colors
                FROM products 
                WHERE status = %s AND stock > 0
                ORDER BY category, name
            """, (status,))
            products = cursor.fetchall()
            # Parse JSON fields
            for p in products:
                if p['images']:
                    p['images'] = json.loads(p['images'])
                if p['colors']:
                    p['colors'] = json.loads(p['colors'])
            return products
        finally:
            cursor.close()
            conn.close()
    
    def get_products_by_category(self, category: str) -> List[Dict]:
        """Get products by category"""
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT id, name, price, compare_at_price, description,
                       images, category, stock, is_free_shipping, colors
                FROM products 
                WHERE status = 'active' AND stock > 0
                AND (category LIKE %s OR collection_name LIKE %s)
                ORDER BY name
            """, (f"%{category}%", f"%{category}%"))
            products = cursor.fetchall()
            for p in products:
                if p['images']:
                    p['images'] = json.loads(p['images'])
                if p['colors']:
                    p['colors'] = json.loads(p['colors'])
            return products
        finally:
            cursor.close()
            conn.close()
    
    def get_product_by_id(self, product_id: str) -> Optional[Dict]:
        """Get a single product by ID"""
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT id, name, price, compare_at_price, description,
                       images, category, stock, is_free_shipping, colors
                FROM products 
                WHERE id = %s
            """, (product_id,))
            product = cursor.fetchone()
            if product:
                if product['images']:
                    product['images'] = json.loads(product['images'])
                if product['colors']:
                    product['colors'] = json.loads(product['colors'])
            return product
        finally:
            cursor.close()
            conn.close()
    
    def search_products(self, query: str) -> List[Dict]:
        """Search products by name or description"""
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            search_term = f"%{query}%"
            cursor.execute("""
                SELECT id, name, price, compare_at_price, description,
                       images, category, stock, is_free_shipping, colors
                FROM products 
                WHERE status = 'active' AND stock > 0
                AND (name LIKE %s OR description LIKE %s OR category LIKE %s)
                ORDER BY name
            """, (search_term, search_term, search_term))
            products = cursor.fetchall()
            for p in products:
                if p['images']:
                    p['images'] = json.loads(p['images'])
                if p['colors']:
                    p['colors'] = json.loads(p['colors'])
            return products
        finally:
            cursor.close()
            conn.close()
    
    def get_categories(self) -> List[str]:
        """Get unique product categories"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT DISTINCT category FROM products 
                WHERE status = 'active' AND stock > 0
                ORDER BY category
            """)
            return [row[0] for row in cursor.fetchall()]
        finally:
            cursor.close()
            conn.close()
    
    # ==================== CUSTOMERS ====================
    
    def get_or_create_customer(self, phone: str, platform: str = "whatsapp") -> Dict:
        """Get existing customer or create new one"""
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            # Try to find existing customer
            cursor.execute("""
                SELECT * FROM customers WHERE phone = %s
            """, (phone,))
            customer = cursor.fetchone()
            
            if not customer:
                # Create new customer
                cursor.execute("""
                    INSERT INTO customers (tenant_id, phone, platform, lifetime_value, created_at, updated_at)
                    VALUES (1, %s, %s, 0, NOW(), NOW())
                """, (phone, platform))
                conn.commit()
                customer_id = cursor.lastrowid
                customer = {
                    'id': customer_id,
                    'phone': phone,
                    'platform': platform,
                    'lifetime_value': 0
                }
            
            return customer
        finally:
            cursor.close()
            conn.close()
    
    # ==================== ORDERS ====================
    
    def create_order(
        self,
        customer_name: str,
        customer_phone: str,
        address: str,
        city: str,
        products: List[Dict],  # [{product_id, quantity, price, name}]
        total_price: float,
        tenant_id: str = "1"
    ) -> str:
        """Create a new COD order"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            order_id = str(uuid.uuid4())
            
            # Get or create customer
            customer = self.get_or_create_customer(customer_phone)
            
            cursor.execute("""
                INSERT INTO orders (
                    id, tenant_id, customer_id, product_data, total_price,
                    status, source_platform, customer_name, customer_phone,
                    address, city, created_at, updated_at
                ) VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, NOW(), NOW()
                )
            """, (
                order_id, tenant_id, str(customer['id']), json.dumps(products), total_price,
                'pending', 'whatsapp', customer_name, customer_phone,
                address, city
            ))
            conn.commit()
            
            # Update customer lifetime value
            cursor.execute("""
                UPDATE customers 
                SET lifetime_value = lifetime_value + %s, updated_at = NOW()
                WHERE id = %s
            """, (total_price, customer['id']))
            conn.commit()
            
            return order_id
        finally:
            cursor.close()
            conn.close()
    
    def get_order(self, order_id: str) -> Optional[Dict]:
        """Get order by ID"""
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
            order = cursor.fetchone()
            if order and order['product_data']:
                order['product_data'] = json.loads(order['product_data'])
            return order
        finally:
            cursor.close()
            conn.close()
    
    # ==================== CONVERSATIONS ====================
    
    def save_message(self, conversation_id: int, sender: str, content: str, msg_type: str = "text"):
        """Save a message to the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO messages (conversation_id, sender, type, content, created_at, updated_at)
                VALUES (%s, %s, %s, %s, NOW(), NOW())
            """, (conversation_id, sender, msg_type, content))
            conn.commit()
        finally:
            cursor.close()
            conn.close()
    
    def get_or_create_conversation(self, customer_id: int, platform: str = "whatsapp") -> int:
        """Get or create a conversation for a customer"""
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            # Find active conversation
            cursor.execute("""
                SELECT id FROM conversations 
                WHERE customer_id = %s AND status = 'active'
                ORDER BY created_at DESC LIMIT 1
            """, (customer_id,))
            conv = cursor.fetchone()
            
            if conv:
                # Update last message time
                cursor.execute("""
                    UPDATE conversations SET last_message_at = NOW() WHERE id = %s
                """, (conv['id'],))
                conn.commit()
                return conv['id']
            
            # Create new conversation
            cursor.execute("""
                INSERT INTO conversations (tenant_id, customer_id, platform, status, last_message_at, created_at, updated_at)
                VALUES (1, %s, %s, 'active', NOW(), NOW(), NOW())
            """, (customer_id, platform))
            conn.commit()
            return cursor.lastrowid
        finally:
            cursor.close()
            conn.close()


# Singleton instance
db = Database()
