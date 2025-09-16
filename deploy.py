#!/usr/bin/env python3
"""
Smart Journal - Deployment Helper Script
"""

import os
import secrets
import subprocess
import sys

def generate_secret_key():
    """Generate a secure secret key"""
    return secrets.token_hex(32)

def check_requirements():
    """Check if all requirements are met"""
    print("🔍 Checking deployment requirements...")
    
    # Check if requirements.txt exists
    if not os.path.exists('requirements.txt'):
        print("❌ requirements.txt not found")
        return False
    
    # Check if app.py exists
    if not os.path.exists('app.py'):
        print("❌ app.py not found")
        return False
    
    # Check if templates directory exists
    if not os.path.exists('templates'):
        print("❌ templates directory not found")
        return False
    
    print("✅ All requirements met!")
    return True

def create_production_env():
    """Create production environment file"""
    print("🔧 Creating production environment configuration...")
    
    secret_key = generate_secret_key()
    jwt_secret = generate_secret_key()
    
    env_content = f"""# Smart Journal Production Environment
# Generated automatically - DO NOT commit this file to version control

# Flask Configuration
SECRET_KEY={secret_key}
FLASK_ENV=production
FLASK_DEBUG=False

# Database Configuration (will be set by hosting provider)
DATABASE_URL=sqlite:///smart_journal.db

# OpenAI API Configuration
# Get your API key from: https://platform.openai.com/api-keys
OPENAI_API_KEY=your_openai_api_key_here

# JWT Configuration
JWT_SECRET_KEY={jwt_secret}

# Security Settings
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Strict

# File Upload Settings
MAX_CONTENT_LENGTH=16777216

# Production Settings
DEBUG=False
TESTING=False
"""
    
    with open('.env.production', 'w') as f:
        f.write(env_content)
    
    print("✅ Production environment file created: .env.production")
    print("📝 Remember to:")
    print("   1. Add your OpenAI API key to .env.production")
    print("   2. Set these environment variables in your hosting platform")
    print("   3. Never commit .env.production to version control")

def create_procfile():
    """Create Procfile for Heroku deployment"""
    print("📄 Creating Procfile for Heroku...")
    
    procfile_content = """web: python run.py
"""
    
    with open('Procfile', 'w') as f:
        f.write(procfile_content)
    
    print("✅ Procfile created")

def create_runtime_file():
    """Create runtime.txt for Python version"""
    print("🐍 Creating runtime.txt...")
    
    runtime_content = """python-3.11.0
"""
    
    with open('runtime.txt', 'w') as f:
        f.write(runtime_content)
    
    print("✅ runtime.txt created")

def check_git_status():
    """Check git status and provide deployment commands"""
    print("📋 Git deployment commands:")
    print("=" * 50)
    print("git add .")
    print("git commit -m 'Deploy Smart Journal to production'")
    print("git push heroku main  # For Heroku")
    print("git push origin main   # For other platforms")
    print("=" * 50)

def main():
    """Main deployment preparation function"""
    print("🚀 Smart Journal - Deployment Preparation")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        print("❌ Deployment requirements not met. Please fix issues above.")
        return
    
    # Create production files
    create_production_env()
    create_procfile()
    create_runtime_file()
    
    print("\n🎉 Deployment preparation complete!")
    print("\n📋 Next steps:")
    print("1. Choose your hosting platform:")
    print("   - Heroku: heroku create your-app-name")
    print("   - Railway: Connect GitHub repo")
    print("   - Render: Connect GitHub repo")
    print("\n2. Set environment variables in your hosting platform:")
    print("   - SECRET_KEY (generated above)")
    print("   - OPENAI_API_KEY (your OpenAI key)")
    print("   - JWT_SECRET_KEY (generated above)")
    print("\n3. Deploy using git commands above")
    
    check_git_status()

if __name__ == "__main__":
    main()
