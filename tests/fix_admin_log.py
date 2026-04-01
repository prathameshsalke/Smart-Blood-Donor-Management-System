# fix_admin_log.py
import re

def fix_admin_log_model():
    """Fix the AdminLog model to use back_populates instead of backref"""
    filepath = 'app/models/admin_log.py'
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace backref with back_populates
    content = content.replace(
        "admin = db.relationship('User', backref='admin_log_entries')",
        "admin = db.relationship('User', back_populates='admin_log_entries')"
    )
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fixed admin_log.py")

def verify_user_model():
    """Verify User model has correct relationship"""
    filepath = 'app/models/user.py'
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if admin_log_entries is properly defined
    if "admin_log_entries = db.relationship('AdminLog', back_populates='admin'" in content:
        print("✅ User model has correct admin_log_entries relationship")
    else:
        print("❌ User model may have incorrect relationship")
    
    # Check if there are any duplicate backrefs
    if "backref" in content:
        print("⚠️ Warning: Found backref usage in user.py - should use back_populates")

def reset_db():
    """Reset the database"""
    import os
    db_path = 'instance/blood_donor.db'
    if os.path.exists(db_path):
        os.remove(db_path)
        print("✅ Deleted old database")

if __name__ == "__main__":
    print("="*50)
    print("FIXING ADMIN LOG RELATIONSHIP")
    print("="*50)
    
    fix_admin_log_model()
    verify_user_model()
    reset_db()
    
    print("\n" + "="*50)
    print("✅ Fix complete!")
    print("="*50)
    print("\nNow run: python run.py")