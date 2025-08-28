#!/usr/bin/env python3
"""
Environment Setup Script for Smart Journal
This script helps you create a .env file with proper configuration.
"""

import os
import secrets

def generate_secret_key():
    """Generate a secure secret key"""
    return secrets.token_hex(32)

def create_env_file():
    """Create .env file with configuration"""
    
    # Check if .env already exists
    if os.path.exists('.env'):
        print("⚠️  .env file already exists!")
        response = input("Do you want to overwrite it? (y/N): ").strip().lower()
        if response != 'y':
            print("❌ Setup cancelled.")
            return
    
    # Generate secure keys
    secret_key = generate_secret_key()
    jwt_secret = generate_secret_key()
    
    # Environment configuration
    env_content = f"""# Smart Journal Environment Configuration
# Generated automatically - DO NOT commit this file to version control

# Flask Configuration
SECRET_KEY={secret_key}
FLASK_ENV=development
FLASK_DEBUG=True

# Database Configuration
DATABASE_URL=sqlite:///smart_journal.db

# OpenAI API Configuration
# Get your API key from: https://platform.openai.com/api-keys
OPENAI_API_KEY=your_openai_api_key_here

# JWT Configuration
JWT_SECRET_KEY={jwt_secret}

# Security Settings
SESSION_COOKIE_SECURE=False
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax

# File Upload Settings
MAX_CONTENT_LENGTH=16777216

# Pagination
POSTS_PER_PAGE=10

# Development Settings
DEBUG=True
TESTING=False

# Production Settings (uncomment and modify for production)
# FLASK_ENV=production
# FLASK_DEBUG=False
# DEBUG=False
# SESSION_COOKIE_SECURE=True
# SESSION_COOKIE_SAMESITE=Strict
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("✅ .env file created successfully!")
        print("\n📋 Next steps:")
        print("1. Edit .env file and add your OpenAI API key")
        print("2. Get your API key from: https://platform.openai.com/api-keys")
        print("3. Never commit .env file to version control")
        print("4. Run your application with: python run.py")
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")

def main():
    print("🔧 Smart Journal Environment Setup")
    print("=" * 40)
    
    create_env_file()

if __name__ == "__main__":
    main()
