# check_admin.py
import sys
import os
from datetime import datetime
import app

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User
from app.models.donor import Donor
from werkzeug.security import check_password_hash, generate_password_hash

def check_admin():
    """Check if admin exists and fix if needed"""
    app = create_app()
    
    with app.app_context():
        print("="*60)
        print("🔍 CHECKING ADMIN USER")
        print("="*60)
        
        # Check all users
        users = User.query.all()
        print(f"\n📊 Total users in database: {len(users)}")
        
        # Check for admin users
        admins = User.query.filter_by(role='admin').all()
        print(f"👑 Admin users found: {len(admins)}")
        
        if admins:
            for admin in admins:
                print(f"\n✅ Admin found:")
                print(f"   ID: {admin.id}")
                print(f"   Name: {admin.name}")
                print(f"   Email: {admin.email}")
                print(f"   Role: {admin.role}")
                print(f"   Active: {admin.is_active}")
                print(f"   Password Hash: {admin.password[:30]}...")
                
                # Test password verification
                test_password = 'Admin@123'
                if admin.check_password(test_password):
                    print(f"   ✅ Password verification successful for: {test_password}")
                else:
                    print(f"   ❌ Password verification failed for: {test_password}")
                    
                    # Reset password
                    admin.set_password('Admin@123')
                    db.session.commit()
                    print(f"   ✅ Password reset to: Admin@123")
        else:
            print("\n❌ No admin user found! Creating new admin...")
            
            # Create new admin
            admin = User(
                email='admin@blooddonor.com',
                name='System Administrator',
                phone='9999999999',
                role='admin',
                is_active=True,
                created_at=datetime.utcnow()
            )
            admin.set_password('Admin@123')
            db.session.add(admin)
            db.session.commit()
            print(f"✅ New admin created:")
            print(f"   Email: admin@blooddonor.com")
            print(f"   Password: Admin@123")
        
        # Check if there are multiple admins
        if len(admins) > 1:
            print(f"\n⚠️ Multiple admin users found ({len(admins)}). Keeping the first one.")
            # Keep the first admin, delete others
            for i, admin in enumerate(admins):
                if i > 0:
                    db.session.delete(admin)
                    print(f"   ❌ Deleted duplicate admin: {admin.email}")
            db.session.commit()
        
        # Final verification
        final_admin = User.query.filter_by(role='admin').first()
        if final_admin:
            print("\n" + "="*60)
            print("✅ ADMIN VERIFICATION COMPLETE")
            print("="*60)
            print(f"\nLogin with these credentials:")
            print(f"   Email: {final_admin.email}")
            print(f"   Password: Admin@123")
            print(f"   Role: {final_admin.role}")
        else:
            print("\n❌ Failed to create/find admin user")

if __name__ == "__main__":
    check_admin()