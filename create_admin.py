from app import app, db, User
from werkzeug.security import generate_password_hash
from datetime import datetime

def create_admin_user():
    with app.app_context():
        # Check if admin user already exists
        admin_user = User.query.filter_by(username='admin').first()
        
        if admin_user:
            print("Admin user already exists!")
            return
        
        # Create new admin user
        admin_user = User(
            username='admin',
            email='admin@mindflow.com',
            password_hash=generate_password_hash('admin123'),
            role='admin',
            created_at=datetime.utcnow(),
            is_active=True
        )
        
        db.session.add(admin_user)
        db.session.commit()
        
        print("Admin user created successfully!")
        print("Username: admin")
        print("Password: admin123")

if __name__ == '__main__':
    create_admin_user()
