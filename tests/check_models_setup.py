# check_models_setup.py
import os
import sys
import app

print("="*50)
print("MODEL SETUP DIAGNOSTIC")
print("="*50)

# Check if instance folder exists
if os.path.exists('instance'):
    print("✅ Instance folder exists")
else:
    print("📁 Creating instance folder...")
    os.makedirs('instance', exist_ok=True)
    print("✅ Instance folder created")

# Check if database file exists
db_path = 'instance/blood_donor.db'
if os.path.exists(db_path):
    print(f"✅ Database file exists ({os.path.getsize(db_path)} bytes)")
else:
    print("❌ Database file does not exist")

print("\n" + "="*50)
print("CREATING DATABASE TABLES")
print("="*50)

try:
    from app import create_app, db
    app = create_app()
    
    with app.app_context():
        # Import all models to ensure they're registered
        from app.models.user import User
        from app.models.donor import Donor
        from app.models.donation import Donation
        from app.models.blood_request import BloodRequest
        from app.models.hospital import Hospital
        from app.models.admin_log import AdminLog
        
        print("✅ All models imported successfully")
        
        # Create all tables
        db.create_all()
        print("✅ Database tables created successfully!")
        
        # Verify tables were created
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"\n📊 Tables in database: {tables}")
        
        if 'donors' in tables:
            print("✅ 'donors' table exists")
        else:
            print("❌ 'donors' table missing")
            
        if 'users' in tables:
            print("✅ 'users' table exists")
        else:
            print("❌ 'users' table missing")
        
        # Create admin user if not exists
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
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*50)
print("Setup complete!")
print("="*50)