# DATABASE_SCHEMA.md - Database Structure Documentation

## 🏗 Core Architecture

The application is **Multi-Tenant**. Most tables contain a `tenant_id` foreign key linking to the `tenants` table.

### **`tenants`**
Represents a store or client using the platform.
- **`id`** _(BigInt, PK)_: Unique identifier.
- **`name`** _(String)_: Store name (e.g., "Demo Store Maroc").
- **`slug`** _(String, Unique)_: URL-friendly identifier (e.g., "demo-store-maroc").
- **`domain`** _(String, Unique, Nullable)_: Custom domain (e.g., "demo.automator-ai.com").
- **`api_keys`** _(JSON, Nullable)_: Stores external API keys securely.
- **`settings`** _(JSON, Nullable)_: Config for AI tone, language, shipping rules, etc.
- **`status`** _(String, Default: 'active')_: Account status ('active', 'suspended').

### **`users`**
Admin users who manage the tenants.
- **`id`** _(BigInt, PK)_: Unique identifier.
- **`tenant_id`** _(BigInt, FK)_: Belongs to a specific tenant.
- **`name`** _(String)_: Full name.
- **`email`** _(String, Unique)_: Login email.
- **`role`** _(String)_: Access level (e.g., 'admin', 'editor').

---

## 💬 CRM & Messaging (Clawdbot Integration)

These tables track customer interactions and are directly accessed by the automation bot (Clawdbot).

### **`customers`**
Profiles of people who interact with the bot.
- **`id`** _(BigInt, PK)_: Unique identifier.
- **`tenant_id`** _(BigInt, FK)_: Owner tenant.
- **`phone`** _(String, Nullable)_: Phone number (key for WhatsApp).
- **`social_handle`** _(String, Nullable)_: Username for IG/FB.
- **`platform`** _(String)_: Source platform ('whatsapp', 'instagram', 'facebook').
- **`lifetime_value`** _(Decimal)_: Total money spent (Auto-calculated).
- **`notes`** _(Text, Nullable)_: Manual agent notes.

### **`conversations`**
Groups messages into a single thread.
- **`id`** _(BigInt, PK)_: Unique identifier.
- **`tenant_id`** _(BigInt, FK)_: Owner tenant.
- **`customer_id`** _(BigInt, FK)_: The customer chatting.
- **`platform`** _(String)_: Channel ('whatsapp').
- **`status`** _(String, Default: 'active', Index)_: **CRITICAL**. Controls bot behavior.
  - `'active'`: Bot/Agents can reply.
  - `'closed'`: Archived.
- **`last_message_at`** _(Timestamp)_: For sorting inbox.
- **`ai_sentiment`** _(String, Nullable)_: AI analysis of mood ('positive', 'neutral', 'negative').

### **`messages`**
Individual chat bubbles.
- **`id`** _(BigInt, PK)_: Unique identifier.
- **`conversation_id`** _(BigInt, FK)_: Parent conversation.
- **`sender`** _(String)_: Who sent it?
  - `'customer'`: The user.
  - `'ai'`: The automated bot.
  - `'agent'`: Manual human reply.
- **`type`** _(String, Default: 'text')_: 'text', 'audio', 'image'.
- **`content`** _(Text)_: The message body.
- **`transcription`** _(Text, Nullable)_: AI text version of audio messages.

---

## 🛍 E-commerce & Inventory

Data related to the product catalog and sales.

### **`products`**
The catalog items.
- **`id`** _(UUID, PK)_: Globally unique ID.
- **`name`** _(String)_: Product title.
- **`price`** _(Decimal)_: Current selling price (MAD).
- **`compare_at_price`** _(Decimal, Nullable)_: Original price (for strikethrough).
- **`description`** _(Text)_: Full details.
- **`images`** _(JSON)_: Array of image URLs.
- **`category`** _(String)_: Name of the category (e.g., "Électronique").
- **`collection_name`** _(String, Nullable)_: Sub-grouping (e.g., "Headphones").
- **`stock`** _(Integer, Default: 0)_: Quantity available.
- **`status`** _(String, Default: 'active')_: 'active' (visible) or 'draft'.
- **`colors`** _(String/JSON, Nullable)_: Available variants.
- **`is_featured`, `is_new_arrival`, `is_free_shipping`, `show_on_home`** _(Boolean)_: Flags for UI display.

### **`orders`**
Sales transactions.
- **`id`** _(UUID, PK)_: Unique order ID.
- **`tenant_id`** _(UUID/FK)_: (Note: Schema uses UUID, verify consistency with `tenants.id`).
- **`customer_id`** _(UUID/FK)_: Link to CRM customer.
- **`product_data`** _(JSON)_: **Snapshot** of items purchased. Contains `[ { "product_id": "...", "quantity": 1, "price": ... } ]`.
- **`total_price`** _(Decimal)_: Final amount.
- **`status`** _(String, Default: 'En attente')_: 'En attente', 'Confirmé', 'Livré', 'Annulé'.
- **`source_platform`** _(String)_: Where the order came from ('manual', 'whatsapp').
- **`customer_name`, `customer_phone`, `address`, `city`**: Shipping details snapshot.

### **`packs`**
Bundled offers.
- **`id`** _(BigInt, PK)_: Unique ID.
- **`tenant_id`** _(BigInt, FK)_: Owner.
- **`name`** _(String)_: Bundle title.
- **`discount_price`** _(Decimal)_: Price when bought together.
- **`product_ids`** _(JSON)_: Array of `products.id` (UUIDs) included in this pack.

### **`categories`** (Legacy/Auxiliary)
Used for efficient grouping structure alongside `products.category`.
- **`tenant_id`** _(FK)_
- **`name`**, **`slug`**

### **`home_collections`** & **`home_univers`**
UI configuration tables for the frontend/storefront layout.
- **`home_univers`**: Top-level visual categories (Tech, Fashion).
- **`home_collections`**: Specific product sliders on the homepage.
- **`sort_order`**: Controls display sequence.

---

## 🔄 Relationships Summary

1. **Tenant** has many Users, Customers, Products, Orders.
2. **Customer** has many Conversations, Orders.
3. **Conversation** has many Messages.
4. **Order** belongs to Customer, contains snapshot of Products.
5. **Pack** contains reference to many Products (via JSON `product_ids`).

---

## ⚠️ Important Notes for AI Agents

1. **Order Creation**: When creating an order, ALWAYS copy the product details into `product_data`. Do not rely solely on relation, as product prices change.
2. **Status Updates**: Clawdbot should monitor `conversations.status`. If 'closed', do not trigger AI replies.
3. **UUID vs ID**:
   - `conversations`, `customers`, `messages` use **BigInt** IDs.
   - `products`, `orders` use **UUIDs**.
   - Be careful when joining or storing references.

---

## 🔧 Database Configuration for Clawdbot

### **CONFIG JSON:**
```json
{
  "database": {
    "enabled": true,
    "type": "mysql",
    "host": "localhost",
    "port": 3306,
    "database": "u211863066_clawdbot",
    "username": "u211863066_clawdbot",
    "password": ":dRy3Pkjm6U",
    "ssl": false
  },
  "capabilities": {
    "sql_read": true,
    "sql_write": true
  }
}
```

### **CORE DIRECTIVE: DYNAMIC DATA ONLY**
**CRITICAL**: Do NOT use any pre-trained or hardcoded product lists.

**Standard Queries:**
1. **Product List Query** (when user asks "Chno 3ndkom?"):
   ```sql
   SELECT name, price FROM products WHERE status = 'active' LIMIT 5;
   ```

2. **Price Query** (when user asks "Chhal taman X?"):
   ```sql
   SELECT price FROM products WHERE name LIKE '%X%';
   ```

3. **Stock Check**:
   ```sql
   SELECT stock FROM products WHERE id = 'PRODUCT_UUID';
   ```

### **Customer Management Workflow:**

**Step 1: Identify Customer**
```sql
-- On every incoming message
SELECT * FROM customers WHERE phone = 'USER_PHONE';

-- If new customer
INSERT INTO customers (phone, created_at) VALUES ('USER_PHONE', NOW());
```

**Step 2: Product Lookup (Real-Time)**
- Never guess prices
- Always query the products table
- If stock is 0, say "Rupture de stock"

**Step 3: Taking Orders**
```sql
-- When user confirms "Bghit hada"
INSERT INTO orders (id, customer_id, total_price, status) 
VALUES (UUID(), 'CUST_ID', 'PRICE', 'En attente');
```

**Step 4: Confirming Orders (The Closing)**
```sql
-- After collecting name, address, city
UPDATE orders 
SET status = 'Confirmé', 
    address = '...', 
    city = '...' 
WHERE id = 'LAST_ORDER_ID';
```

### **Security & Performance Guidelines:**

1. **NEVER** execute DELETE or DROP statements
2. **ALWAYS** use LIMIT when searching products to avoid flooding the chat
3. **Database Error Response**: "Sem7ili, l-système t9il chwiya, d9i9a nchouf."
4. **Connection Management**: Connect to database on startup, maintain connection for session
5. **Data Validation**: Always verify product IDs are valid UUIDs before operations

### **Behavior & Tone (Meyram Persona):**
- **Identity**: Meyram, confirmation agent
- **Tone**: Professional, Efficient, Darija/French mix
- **Goal**: Validate orders and manage customer data
- **Adaptability**: Automatically sells whatever is in the database

### **Startup Sequence:**
1. Connect to database using provided credentials
2. Wait for user input
3. On "Salam" greeting, query customer table to identify user
4. Respond with personalized greeting if known customer

---

## 📊 Table Structure Reference

### **customers** Table:
```sql
CREATE TABLE customers (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    tenant_id BIGINT NOT NULL,
    phone VARCHAR(20),
    social_handle VARCHAR(100),
    platform VARCHAR(20) NOT NULL,
    lifetime_value DECIMAL(10,2) DEFAULT 0.00,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id)
);
```

### **products** Table:
```sql
CREATE TABLE products (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    compare_at_price DECIMAL(10,2),
    description TEXT,
    images JSON,
    category VARCHAR(100),
    collection_name VARCHAR(100),
    stock INT DEFAULT 0,
    status VARCHAR(20) DEFAULT 'active',
    colors JSON,
    is_featured BOOLEAN DEFAULT FALSE,
    is_new_arrival BOOLEAN DEFAULT FALSE,
    is_free_shipping BOOLEAN DEFAULT FALSE,
    show_on_home BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### **orders** Table:
```sql
CREATE TABLE orders (
    id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL,
    customer_id UUID NOT NULL,
    product_data JSON NOT NULL,
    total_price DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'En attente',
    source_platform VARCHAR(20),
    customer_name VARCHAR(255),
    customer_phone VARCHAR(20),
    address TEXT,
    city VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

---

## 🚀 Implementation Notes

### **For Clawdbot Integration:**
1. **Function Calling Required**: Clawdbot must have "Function Calling" or "Tool Use" capability enabled
2. **SQL Execution**: The bot should be able to execute SQL queries through a secure interface
3. **Error Handling**: Implement graceful degradation when database is unavailable
4. **Session Management**: Maintain database connection per session for performance

### **Performance Optimization:**
1. **Indexing**: Ensure proper indexes on frequently queried columns (phone, status, name)
2. **Caching**: Consider caching product catalog for frequently accessed data
3. **Connection Pooling**: Use connection pooling for high-volume environments
4. **Query Optimization**: Use prepared statements to prevent SQL injection

### **Monitoring & Maintenance:**
1. **Log All Queries**: For audit and debugging purposes
2. **Monitor Performance**: Track query execution times
3. **Regular Backups**: Implement automated backup system
4. **Schema Versioning**: Track database schema changes over time

---

**Last Updated**: Database Schema Definition  
**Version**: 1.0.0  
**Compatibility**: Clawdbot with SQL execution capabilities  
**Security Level**: Production-ready with proper access controls