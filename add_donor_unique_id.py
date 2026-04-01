# add_donor_unique_id.py
"""
Script to add donor_unique_id to existing donors
Run: python add_donor_unique_id.py
"""

import sys
import os
import random
import string
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.donor import Donor

def generate_unique_id():
    """Generate unique donor ID"""
    timestamp = datetime.now().strftime('%y%m%d%H%M')
    random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"DNR{timestamp}{random_chars}"

def add_unique_ids_to_donors():
    """Add unique IDs to all existing donors"""
    app = create_app()
    
    with app.app_context():
        print("="*60)
        print("🔑 ADDING UNIQUE IDs TO DONORS")
        print("="*60)
        
        # Get all donors without unique ID
        donors = Donor.query.filter(
            (Donor.donor_unique_id.is_(None)) | 
            (Donor.donor_unique_id == '')
        ).all()
        
        print(f"\nFound {len(donors)} donors without unique ID")
        
        if not donors:
            print("✅ All donors already have unique IDs")
            return
        
        updated = 0
        for donor in donors:
            # Generate unique ID
            donor.donor_unique_id = generate_unique_id()
            updated += 1
            
            if updated % 100 == 0:
                print(f"  Updated {updated} donors...")
                db.session.commit()
        
        db.session.commit()
        print(f"\n✅ Updated {updated} donors with unique IDs")
        
        # Show sample
        sample = Donor.query.first()
        if sample:
            print(f"\nSample donor:")
            print(f"  ID: {sample.id}")
            print(f"  Name: {sample.user.name if sample.user else 'N/A'}")
            print(f"  Unique ID: {sample.donor_unique_id}")

if __name__ == "__main__":
    add_unique_ids_to_donors()