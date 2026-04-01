# complete_fix.py
import os
import shutil

def backup_files():
    """Create backups before fixing"""
    backup_dir = 'backup_models'
    os.makedirs(backup_dir, exist_ok=True)
    
    model_files = ['donor.py', 'user.py', 'donation.py', 'blood_request.py', 'admin_log.py']
    for file in model_files:
        src = f'app/models/{file}'
        dst = f'{backup_dir}/{file}.backup'
        if os.path.exists(src):
            shutil.copy2(src, dst)
            print(f"✅ Backed up {file}")
    
    print(f"📁 Backups saved to {backup_dir}/")

def reset_database():
    """Delete and recreate database"""
    db_path = 'instance/blood_donor.db'
    if os.path.exists(db_path):
        os.remove(db_path)
        print("✅ Deleted old database")
    
    print("\n🔄 Creating new database...")
    try:
        from app import create_app, db
        app = create_app()
        with app.app_context():
            db.create_all()
            print("✅ Database created successfully!")
            
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
            print("✅ Admin user created")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("="*50)
    print("COMPLETE FIX FOR DATABASE ERRORS")
    print("="*50)
    
    print("\n1️⃣ Creating backups...")
    backup_files()
    
    print("\n2️⃣ Please update your model files with the corrected code")
    print("   (Copy the code provided in Fix 1-5)")
    
    input("\nPress Enter after updating the model files...")
    
    print("\n3️⃣ Resetting database...")
    reset_database()
    
    print("\n" + "="*50)
    print("✅ FIX COMPLETE!")
    print("="*50)
    print("\nNow run: python run.py")