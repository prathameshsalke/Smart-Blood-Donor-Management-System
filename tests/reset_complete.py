# reset_complete.py
"""
Complete database reset script
Run this to delete and recreate the database
"""

import os
import shutil
from datetime import datetime

def reset_database():
    """Delete and recreate the database"""
    print("="*50)
    print("COMPLETE DATABASE RESET")
    print("="*50)
    
    # Backup existing database if it exists
    db_path = 'instance/blood_donor.db'
    if os.path.exists(db_path):
        backup_name = f'instance/blood_donor_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
        shutil.copy2(db_path, backup_name)
        print(f"✅ Database backed up to {backup_name}")
        os.remove(db_path)
        print("✅ Old database deleted")
    
    # Ensure instance folder exists
    os.makedirs('instance', exist_ok=True)
    
    try:
        from app import create_app, db
        app = create_app()
        
        with app.app_context():
            # Import all models
            from app.models.user import User
            from app.models.donor import Donor
            from app.models.donation import Donation
            from app.models.blood_request import BloodRequest
            from app.models.hospital import Hospital
            from app.models.admin_log import AdminLog
            
            print("✅ Models imported")
            
            # Create all tables
            db.create_all()
            print("✅ New tables created")
            
            # Create admin user
            admin = User(
                email='admin@blooddonor.com',
                name='Admin User',
                phone='9999999999',
                role='admin'
            )
            admin.set_password('Admin@123')
            db.session.add(admin)
            
            # Create sample donor
            donor_user = User(
                email='donor@test.com',
                name='Test Donor',
                phone='8888888888',
                role='donor'
            )
            donor_user.set_password('Donor@123')
            db.session.add(donor_user)
            db.session.flush()
            
            donor = Donor(
                user_id=donor_user.id,
                blood_type='O+',
                date_of_birth=datetime(1990, 1, 1).date(),
                gender='male',
                weight=70,
                address='123 Test Street',
                city='Mumbai',
                state='Maharashtra',
                pincode='400001',
                emergency_contact_name='Emergency Contact',
                emergency_contact_phone='7777777777',
                emergency_contact_relation='Friend',
                is_available=True
            )
            db.session.add(donor)
            
            # Create sample hospital
            hospital = Hospital(
                name='City Hospital',
                phone='022-12345678',
                address='456 Hospital Road',
                city='Mumbai',
                state='Maharashtra',
                pincode='400002',
                latitude=19.0760,
                longitude=72.8777,
                has_blood_bank=True,
                is_verified=True
            )
            db.session.add(hospital)
            
            db.session.commit()
            print("✅ Sample data created")
            
            # Verify tables
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"\n📊 Tables in database: {tables}")
            
            # Count records
            print(f"\n📊 Record counts:")
            print(f"  Users: {User.query.count()}")
            print(f"  Donors: {Donor.query.count()}")
            print(f"  Hospitals: {Hospital.query.count()}")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "="*50)
    print("✅ RESET COMPLETE!")
    print("="*50)
    print("\nCredentials:")
    print("  Admin: admin@blooddonor.com / Admin@123")
    print("  Donor: donor@test.com / Donor@123")
    print("\nNow run: python run.py")
    return True

if __name__ == "__main__":
    reset_database()
    