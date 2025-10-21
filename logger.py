"""
Simple logging module for the WebSocket chat server.
Handles Unicode encoding issues for Windows compatibility.
"""

import logging
from config import Config

class UnicodeFormatter(logging.Formatter):
    """Formatter that handles Unicode encoding for Windows."""
    
    def format(self, record):
        # Convert messages to ASCII to avoid encoding errors
        if hasattr(record, 'msg'):
            record.msg = str(record.msg).encode('ascii', 'replace').decode('ascii')
        return super().format(record)

# Setup logger
logger = logging.getLogger('chat_server')
logger.setLevel(getattr(logging, Config.LOG_LEVEL))

# Avoid duplicate handlers
if not logger.handlers:
    formatter = UnicodeFormatter(Config.LOG_FORMAT)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler with UTF-8 encoding
    file_handler = logging.FileHandler(Config.LOG_FILE, encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
