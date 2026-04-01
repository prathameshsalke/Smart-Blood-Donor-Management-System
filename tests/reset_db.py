# reset_db.py
import os
import sys

print("="*50)
print("Database Reset Utility")
print("="*50)

# Delete existing database
db_path = 'instance/blood_donor.db'
if os.path.exists(db_path):
    os.remove(db_path)
    print(f"✅ Deleted existing database: {db_path}")
else:
    print(f"ℹ️ No existing database found")

# Recreate database
print("\nCreating new database...")
try:
    from app import create_app, db
    app = create_app()
    
    with app.app_context():
        db.create_all()
        print("✅ Database tables created successfully!")
        
        # Create admin user
        from app.models.user import User
        admin = User(
            email='admin@blooddonor.com',
            name='Admin User',
            phone='9999999999',
            role='admin'
        )
        admin.set_password('Admin@123')
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin user created: admin@blooddonor.com / Admin@123")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*50)
print("Database reset complete!")
print("="*50)