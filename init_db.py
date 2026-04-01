# init_db.py
"""
Database initialization script
Run this to create all database tables
"""

import os
import sys

def init_database():
    """Initialize the database with all tables"""
    print("="*50)
    print("DATABASE INITIALIZATION")
    print("="*50)
    
    # Ensure instance folder exists
    os.makedirs('instance', exist_ok=True)
    print("✅ Instance folder ready")
    
    try:
        from app import create_app, db
        app = create_app()
        
        with app.app_context():
            # Import all models to register them with SQLAlchemy
            from app.models.user import User
            from app.models.donor import Donor
            from app.models.donation import Donation
            from app.models.blood_request import BloodRequest
            from app.models.hospital import Hospital
            from app.models.admin_log import AdminLog
            
            print("✅ Models imported")
            
            # Drop all tables (optional - comment out if you want to keep data)
            # db.drop_all()
            # print("✅ Old tables dropped")
            
            # Create all tables
            db.create_all()
            print("✅ All tables created successfully!")
            
            # Verify tables
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"\n📊 Created tables: {', '.join(tables)}")
            
            # Check if each required table exists
            required_tables = ['users', 'donors', 'donations', 'blood_requests', 'hospitals', 'admin_logs']
            for table in required_tables:
                if table in tables:
                    print(f"  ✅ {table}")
                else:
                    print(f"  ❌ {table}")
            
            # Create admin user
            admin = User.query.filter_by(email='admin@blooddonor.com').first()
            if not admin:
                admin = User(
                    email='admin@blooddonor.com',
                    name='Admin User',
                    phone='9999999999',
                    role='admin'
                )
                admin.set_password('Admin@123')
                db.session.add(admin)
                db.session.commit()
                print("\n✅ Admin user created: admin@blooddonor.com / Admin@123")
            else:
                print("\n✅ Admin user already exists")
            
            # Create a sample donor for testing (optional)
            if User.query.filter_by(email='donor@test.com').first() is None:
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
                db.session.commit()
                print("✅ Sample donor created: donor@test.com / Donor@123")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "="*50)
    print("✅ DATABASE INITIALIZATION COMPLETE")
    print("="*50)
    print("\nNow run: python run.py")
    return True

if __name__ == "__main__":
    # Add datetime import for sample donor
    from datetime import datetime
    init_database()