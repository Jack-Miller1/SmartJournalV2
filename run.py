#!/usr/bin/env python3
"""
MindFlow - Flask Application Startup Script
"""

import os
from app import app, db

if __name__ == '__main__':
    # Set environment
    os.environ['FLASK_ENV'] = 'development'
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Create admin user if not exists
        from app import User
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            from werkzeug.security import generate_password_hash
            admin = User(
                username='admin',
                email='admin@mindflow.com',
                password_hash=generate_password_hash('admin123'),
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
            print("👤 Admin user created: admin / admin123")
        else:
            print("👤 Admin user already exists")
        
        print("✅ Database initialized successfully!")
    
    # Run the application
    print("🚀 Starting MindFlow...")
    print("📍 Access your app at: http://localhost:5000")
    print("👤 Default admin: admin / admin123")
    print("⏹️  Press Ctrl+C to stop")
    
    # Get port from Railway environment variable, default to 5000 for local development
    port = int(os.environ.get('PORT', 5000))
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False  # Set to False for production
    )
