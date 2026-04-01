# test_imports.py
import sys

print("Testing model imports...")

try:
    from app import create_app
    print("✅ create_app imported")
except Exception as e:
    print(f"❌ create_app import failed: {e}")

try:
    from app.models.user import User
    print("✅ User model imported")
except Exception as e:
    print(f"❌ User model import failed: {e}")

try:
    from app.models.donor import Donor
    print("✅ Donor model imported")
except Exception as e:
    print(f"❌ Donor model import failed: {e}")

try:
    from app.models.donation import Donation
    print("✅ Donation model imported")
except Exception as e:
    print(f"❌ Donation model import failed: {e}")

print("\nCreating app instance...")
try:
    app = create_app()
    print("✅ App created")
    
    with app.app_context():
        from app import db
        print("✅ Database imported")
        
        # Try to create tables
        db.create_all()
        print("✅ Tables created")
        
        # Check if tables exist
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"Tables in database: {tables}")
        
        if 'donors' in tables:
            print("✅ donors table exists")
        else:
            print("❌ donors table missing")
            
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()