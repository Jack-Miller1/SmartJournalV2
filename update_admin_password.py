#!/usr/bin/env python3
"""
Script to update admin password
Run this script to change the admin password
"""

import os
from app import app, db, User
from werkzeug.security import generate_password_hash

def update_admin_password(new_password):
    """Update the admin user's password"""
    with app.app_context():
        admin = User.query.filter_by(username='admin').first()
        if admin:
            admin.password_hash = generate_password_hash(new_password)
            db.session.commit()
            print(f"✅ Admin password updated successfully!")
            print(f"👤 New credentials: admin / {new_password}")
        else:
            print("❌ Admin user not found!")

if __name__ == '__main__':
    # Change this to your desired password
    new_password = "YourNewPassword123!"
    update_admin_password(new_password)
