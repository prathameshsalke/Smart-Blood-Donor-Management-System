# complete_reset.py
import os
import shutil
from datetime import datetime

print("="*60)
print("COMPLETE DATABASE AND MODEL RESET")
print("="*60)

# Step 1: Backup existing models
print("\n1️⃣ Backing up existing models...")
backup_dir = 'model_backup_' + datetime.now().strftime('%Y%m%d_%H%M%S')
os.makedirs(backup_dir, exist_ok=True)

if os.path.exists('app/models'):
    for file in os.listdir('app/models'):
        if file.endswith('.py'):
            shutil.copy2(f'app/models/{file}', f'{backup_dir}/{file}')
            print(f"   ✅ Backed up {file}")

# Step 2: Delete old database
print("\n2️⃣ Deleting old database...")
db_path = 'instance/blood_donor.db'
if os.path.exists(db_path):
    os.remove(db_path)
    print("   ✅ Database deleted")
else:
    print("   ℹ️ No database found")

# Step 3: Create new database
print("\n3️⃣ Creating new database...")
try:
    from app import create_app, db
    app = create_app()
    
    with app.app_context():
        db.create_all()
        print("   ✅ Database tables created")
        
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
        print("   ✅ Admin user created")
        
        # Create a test donor
        donor_user = User(
            email='donor@test.com',
            name='Test Donor',
            phone='8888888888',
            role='donor'
        )
        donor_user.set_password('Donor@123')
        db.session.add(donor_user)
        db.session.flush()
        
        from app.models.donor import Donor
        donor = Donor(
            user_id=donor_user.id,
            blood_type='O+',
            date_of_birth=datetime(1990, 1, 1).date(),
            gender='male',
            weight=70,
            address='Test Address',
            city='Test City',
            state='Test State',
            pincode='123456',
            emergency_contact_name='Emergency Contact',
            emergency_contact_phone='7777777777',
            emergency_contact_relation='Friend'
        )
        db.session.add(donor)
        db.session.commit()
        print("   ✅ Test donor created")
        
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("✅ RESET COMPLETE!")
print("="*60)
print("\nNow run: python run.py")
print("\nLogin credentials:")
print("   Admin: admin@blooddonor.com / Admin@123")
print("   Donor: donor@test.com / Donor@123")

from datetime import datetime