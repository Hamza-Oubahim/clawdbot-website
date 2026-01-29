# config.py - Configuration for COD WhatsApp Agent

import os
from dataclasses import dataclass

@dataclass
class Config:
    # Gemini API
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")
    GEMINI_MODEL: str = "gemini-2.0-flash"
    
    # MySQL Database
    DB_HOST: str = "76.13.100.250"
    DB_PORT: int = 5544
    DB_USER: str = "mysql"
    DB_PASSWORD: str = "z4F9eudXRcVPrGq9fyAtZ3lbFpbg0bF8F0jKSUmfVTC2v381D9rXdMBbrRToggoV"
    DB_NAME: str = "default"
    
    # WhatsApp
    WA_SESSION_PATH: str = "./wa_session"
    
    # Agent Settings
    STORE_NAME: str = "Demo Store Maroc"
    CURRENCY: str = "DH"
    
    # Delivery settings
    DEFAULT_DELIVERY_FEE: float = 30.0  # DH
    FREE_DELIVERY_THRESHOLD: float = 500.0  # Free delivery above this amount

config = Config()
