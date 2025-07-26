"""Configuration settings for WhatsApp AI Assistant."""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # WhatsApp API Configuration
    whatsapp_api_token: str = ""
    whatsapp_webhook_verify_token: str = ""
    whatsapp_phone_number_id: str = ""
    
    # OpenAI Configuration
    openai_api_key: str = ""
    openai_model: str = "gpt-3.5-turbo"
    
    # Database Configuration
    database_url: str = "sqlite:///whatsapp_assistant.db"
    
    # Notification Configuration
    smtp_server: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    notification_email: str = ""
    
    # Application Configuration
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Urgency Detection Thresholds
    urgency_keywords: list[str] = [
        "urgent", "emergency", "asap", "immediately", "critical", "help"
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()