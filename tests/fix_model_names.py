# fix_model_names.py
import re
import os

def fix_donor_model():
    """Fix relationship names in donor model"""
    filepath = 'app/models/donor.py'
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace any 'user_account' with 'user'
    content = content.replace('user_account', 'user')
    
    # Ensure the relationship is properly defined
    if 'user = db.relationship' not in content:
        # Add the relationship if missing
        rel_code = """
    # Relationship
    user = db.relationship('User', back_populates='donor_profile', uselist=False)
"""
        # Insert after user_id line
        content = content.replace(
            'user_id = db.Column(db.Integer, db.ForeignKey(\'users.id\'), unique=True, nullable=False)',
            'user_id = db.Column(db.Integer, db.ForeignKey(\'users.id\'), unique=True, nullable=False)' + rel_code
        )
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fixed donor.py")

def fix_user_model():
    """Ensure user model has correct back_populates"""
    filepath = 'app/models/user.py'
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Make sure donor_profile uses back_populates='user'
    pattern = r"donor_profile = db\.relationship\(\s*'Donor',\s*([^)]*)\)"
    
    def replace_donor_profile(match):
        args = match.group(1)
        if 'back_populates' not in args:
            args = args.rstrip() + ", back_populates='user'"
        return f"donor_profile = db.relationship('Donor', {args})"
    
    content = re.sub(pattern, replace_donor_profile, content, flags=re.DOTALL)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fixed user.py")

def reset_db():
    """Reset the database"""
    import os
    db_path = 'instance/blood_donor.db'
    if os.path.exists(db_path):
        os.remove(db_path)
        print("✅ Deleted old database")

if __name__ == "__main__":
    print("="*50)
    print("FIXING MODEL RELATIONSHIP NAMES")
    print("="*50)
    
    fix_donor_model()
    fix_user_model()
    reset_db()
    
    print("\n" + "="*50)
    print("✅ Fix complete! Now run:")
    print("python run.py")
    print("="*50)