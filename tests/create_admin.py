# tests/create_admin.py
import sys
import os

# Add the project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.user import User
from datetime import datetime

def create_admin():
    """Create or reset admin user"""
    app = create_app()
    with app.app_context():
        # Check if admin exists
        admin = User.query.filter_by(email='admin@blooddonor.com').first()
        
        if admin:
            print(f"✅ Admin already exists: {admin.email}")
            # Reset password just in case
            admin.set_password('Admin@123')
            db.session.commit()
            print("✅ Admin password reset to: Admin@123")
        else:
            # Create new admin
            admin = User(
                email='admin@blooddonor.com',
                name='Admin User',
                phone='9999999999',
                role='admin',
                is_active=True,
                created_at=datetime.utcnow()
            )
            admin.set_password('Admin@123')
            db.session.add(admin)
            db.session.commit()
            print("✅ New admin created successfully!")
        
        # Verify
        verify = User.query.filter_by(email='admin@blooddonor.com').first()
        if verify and verify.check_password('Admin@123'):
            print("\n✅ Admin verification successful!")
            print(f"   Email: admin@blooddonor.com")
            print(f"   Password: Admin@123")
            print(f"   Role: {verify.role}")
        else:
            print("\n❌ Admin verification failed!")

if __name__ == "__main__":
    create_admin()