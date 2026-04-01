# fix_relationships.py
import os
import re

def fix_all_models():
    """Fix all relationship naming conflicts"""
    
    fixes = [
        # File path, pattern to find, replacement
        ('app/models/user.py', 
         r"donor_profile = db\.relationship\('Donor', backref='user'",
         "donor_profile = db.relationship('Donor', backref='user_account'"),
        
        ('app/models/user.py',
         r"donations = db\.relationship\('Donation', backref='donor_user'",
         "donations = db.relationship('Donation', backref='donor_account'"),
        
        ('app/models/user.py',
         r"requests = db\.relationship\('BloodRequest', backref='requester'",
         "requests = db.relationship('BloodRequest', backref='requester_account'"),
        
        ('app/models/user.py',
         r"admin_logs = db\.relationship\('AdminLog', backref='admin'",
         "admin_logs = db.relationship('AdminLog', backref='admin_user'"),
        
        ('app/models/user.py',
         r"verified_donations = db\.relationship\('Donation', backref='verifier_user'",
         "verified_donations = db.relationship('Donation', backref='verifier_account'"),
        
        ('app/models/donation.py',
         r"donor = db\.relationship\('User', foreign_keys=\[donor_id\], backref='donations_made'",
         "donor = db.relationship('User', foreign_keys=[donor_id], backref='donations_list'"),
        
        ('app/models/donation.py',
         r"verifier = db\.relationship\('User', foreign_keys=\[verified_by\], backref='verified_donations'",
         "verifier = db.relationship('User', foreign_keys=[verified_by], backref='verified_donations_list'"),
        
        ('app/models/admin_log.py',
         r"admin = db\.relationship\('User', backref='admin_logs'",
         "admin = db.relationship('User', backref='admin_log_entries'"),
    ]
    
    for filepath, pattern, replacement in fixes:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            new_content = re.sub(pattern, replacement, content)
            
            if new_content != content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"✅ Fixed: {filepath}")
            else:
                print(f"ℹ️ No changes needed: {filepath}")
        else:
            print(f"❌ File not found: {filepath}")

if __name__ == "__main__":
    print("="*50)
    print("Fixing Relationship Naming Conflicts")
    print("="*50)
    fix_all_models()
    print("="*50)
    print("Done! Now reset your database.")