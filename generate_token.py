#!/usr/bin/env python3
"""
Script to generate a secure token for the WebSocket chat authentication.
"""

import secrets
import string
import sys

def generate_secure_token(length=32):
    """Génère un token sécurisé aléatoire."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_hex_token(length=32):
    """Génère un token hexadécimal sécurisé."""
    return secrets.token_hex(length)

if __name__ == "__main__":
    print("Secure token generator for the WebSocket chat")
    print("=" * 50)
    
    # Génération de différents types de tokens
    print(f"Alphanumeric token (32 chars): {generate_secure_token()}")
    print(f"Hexadecimal token (32 chars): {generate_hex_token()}")
    print(f"Hexadecimal token (64 chars): {generate_hex_token(32)}")
    
    print("\n To use a token :")
    print("1. Copy one of the tokens above")
    print("2. Add it to your .env file :")
    print("   SECRET_TOKEN=your_token_here")
    print("3. Restart the server")
    
    print("\n  Important : Keep this token secret and do not share it!")
