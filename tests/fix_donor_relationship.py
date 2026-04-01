# fix_donor_relationship.py
import re

def fix_donor_model():
    """Remove the problematic relationship and add property"""
    filepath = 'app/models/donor.py'
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove the problematic relationship
    pattern = r'donation_history = db\.relationship\(.*?lazy=\'dynamic\'\).*?\n'
    content = re.sub(pattern, '', content, flags=re.DOTALL)
    
    # Add property after the relationships section
    property_code = """
    @property
    def donation_history(self):
        \"\"\"Get donation history through the associated user\"\"\"
        if hasattr(self, 'user_account') and self.user_account:
            return self.user_account.donations_list
        return []
"""
    
    # Find where to insert the property
    insert_point = content.find('# Timestamps')
    if insert_point != -1:
        content = content[:insert_point] + property_code + '\n' + content[insert_point:]
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fixed donor.py")

def update_user_model():
    """Update user model to use back_populates"""
    filepath = 'app/models/user.py'
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace backref with back_populates
    content = content.replace("backref='user_account'", "back_populates='user_account'")
    content = content.replace("backref='donor_account'", "back_populates='donor'")
    content = content.replace("backref='requester_account'", "back_populates='requester'")
    content = content.replace("backref='admin_user'", "back_populates='admin'")
    content = content.replace("backref='verifier_account'", "back_populates='verifier'")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fixed user.py")

def update_donation_model():
    """Update donation model to use back_populates"""
    filepath = 'app/models/donation.py'
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace backref with back_populates
    content = content.replace("backref='donations_list'", "back_populates='donations_list'")
    content = content.replace("backref='verified_donations_list'", "back_populates='verified_donations_list'")
    content = content.replace("backref='donation_list'", "back_populates='donations'")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fixed donation.py")

def reset_database():
    """Reset the database"""
    import os
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
    print("FIXING DONOR RELATIONSHIP ERROR")
    print("="*50)
    
    print("\n1️⃣ Fixing model files...")
    fix_donor_model()
    update_user_model()
    update_donation_model()
    
    print("\n2️⃣ Resetting database...")
    reset_database()
    
    print("\n" + "="*50)
    print("✅ FIX COMPLETE!")
    print("="*50)
    print("\nNow run: python run.py")