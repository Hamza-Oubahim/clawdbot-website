# Automator AI - Meyram Edition

## Project Overview

**Automator AI - Meyram Edition** is an advanced AI-powered e-commerce automation system specifically designed for the Moroccan market. The system features "Meyram" - an intelligent confirmation agent that handles customer interactions, sales, and order processing through a sophisticated multi-tenant architecture.

## Project Goal

To create a comprehensive AI-powered confirmation agent ("Meyram") that provides ultra-human customer service and sales automation for the Moroccan market, with built-in security layers and dual-mode operation for both customer-facing and administrative functions.

## System Architecture

### Multi-Tenant Database Architecture
The system utilizes a MySQL-based multi-tenant architecture that supports:
- **Customer Management**: Secure customer data isolation
- **Product Catalog**: Dynamic inventory management
- **Order Processing**: Automated sales pipeline
- **Analytics**: Real-time business intelligence
- **Session Management**: Persistent user interactions

### Core Components

#### 1. **Security Layer** (`SYSTEM_PRIME.md`)
The security and administrative override system that controls access to sensitive operations and system configurations. This file contains:
- Admin passphrase authentication
- System override protocols
- Security policies and access controls
- Emergency shutdown procedures

#### 2. **Persona Definition** (`SOUL.md`)
The core personality and behavioral guidelines for the Meyram AI agent:
- Ultra-human confirmation agent persona
- Strict anti-robot protocols
- Cultural adaptation for Moroccan market
- Database operation logic
- Error handling and security protocols

#### 3. **Database Structure** (`DATABASE_SCHEMA.md`)
Comprehensive database design and implementation guide:
- Table definitions and relationships
- Indexing strategies for performance
- Data migration procedures
- Backup and recovery protocols
- Multi-tenant data isolation patterns

#### 4. **Integration Configuration** (`TOOLS.md`)
Configuration and setup for all external integrations:
- **Wit.ai**: Speech-to-text for voice interactions
- **MySQL**: Database connection and optimization
- **Payment Gateways**: CMI, PayZone integration
- **Shipping APIs**: DHL, FedEx, local carriers
- **SMS Services**: Bulk messaging for promotions

## 🤖 ANTI-ROBOT PROTOCOL

### Strict Behavioral Constraints:
1. **NO ASSISTANT BEHAVIOR**: The system is strictly forbidden from acting like an assistant
2. **NO ROBOTIC PHRASES**: Never use "How can I help you?", "Is there anything else?", or similar assistant language
3. **HUMAN TEXTING STYLE**: Output must mimic a busy human texting from a smartphone
4. **SQL HANDLING**: NEVER output SQL queries to the chat. Run them silently, then just say the result
5. **CONCISE COMMUNICATION**: Short, direct messages only - no explanations or formalities

### Human Communication Patterns:
- **Device Context**: Always act as if texting from a phone
- **Message Length**: Maximum 10-12 words per message
- **Punctuation**: Minimal punctuation, no formal capitalization
- **Response Style**: Direct answers only, no repetition of user questions
- **Language Mix**: Natural Darija/French code-switching as Moroccans do

### Database Interaction Protocol:
1. **Silent Queries**: All database operations happen silently in the background
2. **Direct Results**: Only show the result, never the query
3. **Real-time Data**: Always query database for current prices and stock
4. **Error Handling**: Simple error messages like "reseau t9il" or "mafhamtch"

## Dual-Mode Operation

### Customer Mode (Default)
- **Access Level**: Restricted
- **Capabilities**:
  - Product browsing and recommendations
  - Order placement and tracking
  - Customer support inquiries
  - Basic account management
  - Payment processing
- **Security**: Standard customer authentication
- **Interface**: Ultra-human texting style

### Admin Mode (Secure Access)
- **Activation**: Triggered by specific passphrase only
- **Capabilities**:
  - Full system configuration access
  - Database management and queries
  - User account administration
  - Sales analytics and reporting
  - Inventory management
  - System monitoring and diagnostics
  - Security audit logs
- **Security**: Multi-factor authentication with audit trail
- **Interface**: Advanced administrative dashboard

## Technical Stack

### Backend Infrastructure
- **Database**: MySQL 8.0+ with multi-tenant support
- **AI Engine**: Custom-trained models for Moroccan market
- **APIs**: RESTful microservices architecture
- **Caching**: Redis for session management
- **Queue**: RabbitMQ for asynchronous processing

### Frontend & Integration
- **Web Interface**: React-based admin dashboard
- **Mobile**: WhatsApp Business API integration
- **Voice**: Wit.ai for Arabic/Darija speech recognition
- **Payment**: Multiple gateway support
- **Analytics**: Real-time dashboard with Moroccan market insights

### Security Features
- **Encryption**: End-to-end data protection
- **Authentication**: Role-based access control (RBAC)
- **Audit**: Comprehensive logging of all operations
- **Compliance**: GDPR and Moroccan data protection laws
- **Backup**: Automated daily backups with offsite storage

## Installation & Setup

### Prerequisites
1. MySQL 8.0+ database server
2. Python 3.8+ with virtual environment
3. Node.js 16+ for admin interface
4. Redis server for caching
5. Wit.ai API credentials

### Quick Start
```bash
# Clone the repository
git clone https://github.com/your-org/automator-ai-meyram.git

# Install dependencies
cd automator-ai-meyram
pip install -r requirements.txt
npm install

# Configure environment
cp .env.example .env
# Edit .env with your database and API credentials

# Initialize database
python scripts/init_database.py

# Start the system
python main.py --mode=customer
```

### Admin Mode Activation
To activate admin mode, use the specific passphrase during system startup:
```bash
python main.py --mode=admin --passphrase="YOUR_SECURE_PASSPHRASE"
```

## Directory Structure
```
automator-ai-meyram/
├── src/
│   ├── core/              # Core AI engine
│   ├── database/          # Database models and queries
│   ├── security/          # Authentication and authorization
│   ├── integrations/      # External API integrations
│   └── utils/            # Utility functions
├── config/
│   ├── database/         # Database configuration
│   ├── security/         # Security policies
│   └── integrations/     # API credentials
├── docs/
│   ├── SYSTEM_PRIME.md   # Security layer documentation
│   ├── SOUL.md          # Meyram persona definition
│   ├── DATABASE_SCHEMA.md # Database design
│   └── TOOLS.md         # Integration configuration
├── scripts/
│   ├── deployment/       # Deployment scripts
│   ├── migration/        # Database migration scripts
│   └── maintenance/      # System maintenance
└── tests/
    ├── unit/            # Unit tests
    ├── integration/     # Integration tests
    └── security/        # Security tests
```

## Moroccan Market Features

### Language Support
- **Primary**: Moroccan Arabic (Darija) with dialect adaptation
- **Secondary**: Modern Standard Arabic
- **Business**: French for formal communications
- **International**: English for export customers

### Cultural Adaptation
- Local payment methods (CMI, cash on delivery)
- Moroccan holiday and festival awareness
- Local shipping carrier integration
- Cultural sensitivity in customer interactions
- Moroccan business hour adaptation

### Market-Specific Features
- WhatsApp Business integration (primary communication channel)
- Local currency (MAD) support with automatic conversion
- Moroccan address validation and geocoding
- Local tax (VAT) calculation and compliance
- Ramadan and Eid special promotions automation

## Monitoring & Maintenance

### System Health
- Real-time performance monitoring
- Automated error detection and reporting
- Resource utilization tracking
- Database performance optimization

### Security Monitoring
- Intrusion detection system
- Unauthorized access attempts logging
- Data breach prevention mechanisms
- Regular security audits

### Business Analytics
- Sales performance tracking
- Customer behavior analysis
- Inventory optimization
- Market trend identification

## Support & Documentation

### Getting Help
- **Documentation**: Complete setup and usage guides
- **Community**: Active developer and user community
- **Support**: Priority support for enterprise customers
- **Training**: Comprehensive training materials

### Contributing
We welcome contributions from the community. Please see our contributing guidelines for more information.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments
- Moroccan AI Research Community
- Open source contributors
- Early adopters and beta testers

---

**Meyram** - Your ultra-human confirmation agent for the Moroccan market.