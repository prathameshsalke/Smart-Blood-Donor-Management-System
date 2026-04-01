# quick_fix_models.py
import re
import os

def fix_donor_model():
    filepath = 'app/models/donor.py'
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Fix the relationship line
    pattern = r"donation_history = db\.relationship\('Donation', backref='donor_profile', lazy='dynamic'\)"
    replacement = "donation_history = db.relationship('Donation', backref='donor_profile', foreign_keys='Donation.donor_id', lazy='dynamic')"
    
    new_content = re.sub(pattern, replacement, content)
    
    with open(filepath, 'w') as f:
        f.write(new_content)
    print("✅ Fixed donor.py")

def fix_donation_model():
    filepath = 'app/models/donation.py'
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Ensure foreign keys are properly defined
    if 'donor_id = db.Column(db.Integer, db.ForeignKey' not in content:
        print("❌ donation.py needs manual fixing")
    else:
        print("✅ donation.py looks good")

def fix_user_model():
    filepath = 'app/models/user.py'
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Fix donor_profile relationship
    pattern = r"donor_profile = db\.relationship\('Donor', backref='user', uselist=False, cascade='all, delete-orphan'\)"
    replacement = "donor_profile = db.relationship('Donor', backref='user', uselist=False, cascade='all, delete-orphan', foreign_keys='Donor.user_id')"
    
    new_content = re.sub(pattern, replacement, content)
    
    # Fix donations relationship
    pattern2 = r"donations = db\.relationship\('Donation', backref='donor_user'\)"
    replacement2 = "donations = db.relationship('Donation', backref='donor_user', foreign_keys='Donation.donor_id')"
    
    new_content = re.sub(pattern2, replacement2, new_content)
    
    with open(filepath, 'w') as f:
        f.write(new_content)
    print("✅ Fixed user.py")

if __name__ == "__main__":
    fix_donor_model()
    fix_donation_model()
    fix_user_model()
    print("\n✅ All models fixed! Now reset your database.")