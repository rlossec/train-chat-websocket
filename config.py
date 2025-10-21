"""
Configuration module for the WebSocket chat server.
Centralizes all configuration settings and environment variables.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the chat server."""
    
    # Server configuration
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 8080))
    
    # Security configuration
    SECRET_TOKEN = os.getenv('SECRET_TOKEN')

    # Configuration de sécurité

    MAX_MESSAGE_LENGTH = 500
    MAX_CONNECTIONS = 100
    RATE_LIMIT_PER_MINUTE = 60
    
    # Logging configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    LOG_FILE = os.getenv('LOG_FILE', 'chat_server.log')
    
    # Validation
    @classmethod
    def validate(cls):
        """Validate configuration settings."""
        if not cls.SECRET_TOKEN:
            raise ValueError("SECRET_TOKEN is not set in environment variables")
        
        if cls.SECRET_TOKEN == 'your_secure_token_here':
            raise ValueError("Please set a proper SECRET_TOKEN in your .env file")
        
        if len(cls.SECRET_TOKEN) < 8:
            raise ValueError("SECRET_TOKEN must be at least 8 characters long")
    
    @classmethod
    def get_server_url(cls):
        """Get the WebSocket server URL."""
        return f"ws://{cls.HOST}:{cls.PORT}"
    
    @classmethod
    def get_connection_url(cls, token: str = None):
        """Get the full connection URL with token."""
        if token is None:
            token = cls.SECRET_TOKEN
        return f"ws://{cls.HOST}:{cls.PORT}/ws?token={token}"

# Validate configuration on import
Config.validate()
