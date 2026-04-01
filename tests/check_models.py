# check_models.py
import sys
import os


print("="*50)
print("MODEL DIAGNOSTIC TOOL")
print("="*50)

try:
    from app import create_app
    app = create_app()
    print("✅ App created successfully")
except Exception as e:
    print(f"❌ Error creating app: {e}")
    sys.exit(1)

with app.app_context():
    print("\n📊 Checking models...")
    
    # Check Donor model
    try:
        from app.models.donor import Donor
        print("✅ Donor model imported")
        
        # Check relationships
        print("\n   Donor relationships:")
        if hasattr(Donor, 'user'):
            print("   ✅ Donor has 'user' relationship")
        else:
            print("   ❌ Donor missing 'user' relationship")
            
        if hasattr(Donor, 'donation_history'):
            print("   ✅ Donor has 'donation_history' property")
        else:
            print("   ❌ Donor missing 'donation_history' property")
            
    except Exception as e:
        print(f"❌ Error with Donor model: {e}")
    
    # Check User model
    try:
        from app.models.user import User
        print("\n✅ User model imported")
        
        # Check relationships
        print("   User relationships:")
        if hasattr(User, 'donor_profile'):
            print("   ✅ User has 'donor_profile' relationship")
        else:
            print("   ❌ User missing 'donor_profile' relationship")
            
        if hasattr(User, 'donations_list'):
            print("   ✅ User has 'donations_list' relationship")
        else:
            print("   ❌ User missing 'donations_list' relationship")
            
    except Exception as e:
        print(f"❌ Error with User model: {e}")
    
    # Check Donation model
    try:
        from app.models.donation import Donation
        print("\n✅ Donation model imported")
        
        # Check relationships
        print("   Donation relationships:")
        if hasattr(Donation, 'donor'):
            print("   ✅ Donation has 'donor' relationship")
        else:
            print("   ❌ Donation missing 'donor' relationship")
            
    except Exception as e:
        print(f"❌ Error with Donation model: {e}")
    
    # Try to create tables
    print("\n🔄 Attempting to create tables...")
    try:
        from app import db
        db.create_all()
        print("✅ Tables created successfully")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")

print("\n" + "="*50)
print("Diagnostic complete")
print("="*50)