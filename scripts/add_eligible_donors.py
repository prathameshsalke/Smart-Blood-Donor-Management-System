# scripts/add_eligible_donors.py
"""
Script to add 1000 eligible blood donors to the database
Run: python scripts/add_eligible_donors.py
"""

import sys
import os
import random
import uuid
from datetime import datetime, timedelta

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now import from app
from app import create_app, db
from app.models.user import User
from app.models.donor import Donor
from app.models.donation import Donation

# ==================== SAMPLE DATA ====================

FIRST_NAMES = [
    'Raj', 'Priya', 'Amit', 'Sunita', 'Vikram', 'Neha', 'Rahul', 'Pooja', 'Sanjay', 'Anita',
    'Deepak', 'Kavita', 'Manoj', 'Rekha', 'Suresh', 'Meena', 'Ramesh', 'Geeta', 'Mahesh', 'Sneha',
    'Ashok', 'Nisha', 'Vijay', 'Shweta', 'Pankaj', 'Jyoti', 'Anil', 'Sarita', 'Nitin', 'Kiran',
    'Rajesh', 'Divya', 'Sunil', 'Anjali', 'Ajay', 'Ritu', 'Arun', 'Shilpa', 'Vivek', 'Pallavi',
    'Jatin', 'Monika', 'Gaurav', 'Shalini', 'Tarun', 'Richa', 'Naveen', 'Babita', 'Kunal', 'Sapna'
]

LAST_NAMES = [
    'Sharma', 'Verma', 'Patel', 'Kumar', 'Singh', 'Gupta', 'Joshi', 'Malhotra', 'Reddy', 'Yadav',
    'Mehta', 'Choudhary', 'Mishra', 'Thakur', 'Saxena', 'Trivedi', 'Desai', 'Menon', 'Nair', 'Pillai',
    'Rao', 'Naidu', 'Prasad', 'Sinha', 'Das', 'Ghosh', 'Banerjee', 'Chatterjee', 'Mukherjee', 'Bose'
]

CITIES_STATES = [
    ('Mumbai', 'Maharashtra', 19.0760, 72.8777),
    ('Delhi', 'Delhi', 28.6139, 77.2090),
    ('Bangalore', 'Karnataka', 12.9716, 77.5946),
    ('Chennai', 'Tamil Nadu', 13.0827, 80.2707),
    ('Kolkata', 'West Bengal', 22.5726, 88.3639),
    ('Hyderabad', 'Telangana', 17.3850, 78.4867),
    ('Pune', 'Maharashtra', 18.5204, 73.8567),
    ('Ahmedabad', 'Gujarat', 23.0225, 72.5714),
    ('Jaipur', 'Rajasthan', 26.9124, 75.7873),
    ('Lucknow', 'Uttar Pradesh', 26.8467, 80.9462),
]

BLOOD_TYPES = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
GENDERS = ['male', 'female', 'other']

DONATION_CENTERS = [
    'Red Cross Blood Bank', 'Rotary Blood Bank', 'Lions Club Blood Bank', 'Indian Blood Bank',
    'City Blood Bank', 'District Hospital Blood Bank', 'Medical College Blood Bank',
    'Private Blood Bank', 'Community Blood Center', 'Mobile Blood Donation Camp'
]

# ==================== HELPER FUNCTIONS ====================

def random_date(start_year=1970, end_year=2005):
    """Generate random date"""
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    return start + timedelta(days=random.randint(0, (end - start).days))

def random_date_recent(start_days_ago=90, end_days_ago=365):
    """Generate random date in the past (for eligible donors - more than 90 days ago)"""
    days_ago = random.randint(end_days_ago, start_days_ago)
    return datetime.now() - timedelta(days=days_ago)

def random_phone():
    """Generate random 10-digit phone number"""
    return f"{random.choice([6,7,8,9])}{random.randint(100000000, 999999999)}"

def random_email(first_name, last_name):
    """Generate random email"""
    domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'rediffmail.com']
    number = random.randint(1, 999)
    return f"{first_name.lower()}.{last_name.lower()}{number}@{random.choice(domains)}"

def random_address():
    """Generate random address"""
    streets = ['Main Street', 'Park Avenue', 'MG Road', 'Linking Road', 'Church Street',
               'Commercial Street', 'Brigade Road', 'Residency Road', 'Cunningham Road']
    return f"{random.randint(1, 999)}, {random.choice(streets)}"

def random_pincode():
    """Generate random 6-digit pincode"""
    return f"{random.randint(100000, 999999)}"

def generate_unique_donation_id():
    """Generate truly unique donation ID"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    unique_id = str(uuid.uuid4()).replace('-', '')[:8].upper()
    return f"DON{timestamp}{unique_id}"

# ==================== MAIN FUNCTION ====================

def add_eligible_donors(count=1000):
    """Add exactly 1000 eligible donors"""
    app = create_app()
    
    with app.app_context():
        print("="*70)
        print(f"🩸 ADDING {count} ELIGIBLE DONORS")
        print("="*70)
        
        # Check existing donors
        existing_count = Donor.query.count()
        print(f"\n📊 Current donors in database: {existing_count}")
        
        # Confirm
        response = input(f"\nAdd {count} eligible donors? (yes/no): ")
        if response.lower() != 'yes':
            print("❌ Operation cancelled")
            return
        
        start_time = datetime.now()
        created = 0
        batch_size = 50
        
        print(f"\n🚀 Starting to add {count} eligible donors...\n")
        
        for batch_start in range(0, count, batch_size):
            batch_end = min(batch_start + batch_size, count)
            
            for i in range(batch_start, batch_end):
                # Generate donor data
                first = random.choice(FIRST_NAMES)
                last = random.choice(LAST_NAMES)
                name = f"{first} {last}"
                email = random_email(first, last)
                phone = random_phone()
                
                # Random city
                city_data = random.choice(CITIES_STATES)
                
                # Generate age between 18 and 55 (prime donation age)
                age = random.randint(18, 55)
                birth_year = datetime.now().year - age
                birth_date = datetime(birth_year, random.randint(1, 12), random.randint(1, 28)).date()
                
                # Create user
                user = User(
                    email=email,
                    name=name,
                    phone=phone,
                    role='donor',
                    is_active=True,
                    created_at=random_date(2022, 2025)
                )
                user.set_password('Donor@123')
                db.session.add(user)
                db.session.flush()
                
                # Generate random coordinates near city
                lat = city_data[2] + random.uniform(-0.3, 0.3)
                lon = city_data[3] + random.uniform(-0.3, 0.3)
                
                # ALL DONORS ARE ELIGIBLE - last donation > 90 days ago
                is_eligible = True
                is_available = random.choice([True, False])  # Some available, some not
                
                # Give them some donation history (1-10 donations)
                total_donations = random.randint(1, 10)
                
                # Last donation was > 90 days ago (to maintain eligibility)
                last_donation_date = random_date_recent(100, 500)  # Between 100-500 days ago
                
                # Create donor profile
                donor = Donor(
                    user_id=user.id,
                    blood_type=random.choice(BLOOD_TYPES),
                    date_of_birth=birth_date,
                    gender=random.choice(GENDERS),
                    weight=random.randint(50, 95),  # Healthy weight range
                    address=random_address(),
                    city=city_data[0],
                    state=city_data[1],
                    pincode=random_pincode(),
                    latitude=lat,
                    longitude=lon,
                    location_updated_at=datetime.utcnow(),
                    medical_conditions=random.choice([None, None, None, 'Mild Asthma', 'Controlled BP']),
                    medications=random.choice([None, None, None, 'None', 'None']),
                    last_donation_date=last_donation_date,
                    total_donations=total_donations,
                    is_available=is_available,
                    is_eligible=is_eligible,
                    emergency_contact_name=f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
                    emergency_contact_phone=random_phone(),
                    emergency_contact_relation=random.choice(['Spouse', 'Parent', 'Sibling', 'Friend', 'Child']),
                    nationality='Indian',
                    has_disability=random.choice([False, False, False, True]),  # 25% have disability
                    disability=random.choice([None, None, None, 'Mobility impairment']),
                    profile_photo=None,
                    created_at=user.created_at
                )
                db.session.add(donor)
                db.session.flush()
                
                # Create donation records for history (1-3 records)
                donation_count = min(total_donations, 3)  # Limit to 3 for performance
                donation_dates = []
                
                # Generate spread out donation dates
                for d in range(donation_count):
                    if d == 0:
                        # Most recent donation (the last_donation_date)
                        donation_date = last_donation_date
                    else:
                        # Older donations
                        days_offset = random.randint(200, 800)
                        donation_date = last_donation_date - timedelta(days=days_offset)
                    
                    donation_dates.append(donation_date)
                
                # Sort dates (oldest first)
                donation_dates.sort()
                
                for donation_date in donation_dates:
                    donation = Donation(
                        donor_id=user.id,
                        donor_name=user.name,
                        donor_blood_type=donor.blood_type,
                        donation_date=donation_date,
                        units_donated=random.randint(1, 2),
                        donation_center=random.choice(DONATION_CENTERS),
                        is_verified=random.choice([True, False, True]),  # Mostly verified
                        certificate_generated=random.choice([True, True, False]),
                        blood_pressure=f"{random.randint(110, 130)}/{random.randint(70, 90)}",
                        hemoglobin_level=round(random.uniform(12.5, 16.5), 1)
                    )
                    
                    # Set unique donation ID
                    donation.donation_id = generate_unique_donation_id()
                    db.session.add(donation)
                
                created += 1
                
                # Progress indicator
                if created % 10 == 0:
                    print(f"  ✓ Created {created} eligible donors...")
            
            # Commit batch
            db.session.commit()
            print(f"✅ Batch {batch_end}/{count} committed")
        
        # Final statistics
        elapsed = datetime.now() - start_time
        print(f"\n{'='*70}")
        print(f"✅ SUCCESSFULLY ADDED {created} ELIGIBLE DONORS!")
        print(f"⏱️  Time taken: {elapsed.total_seconds():.1f} seconds")
        print(f"{'='*70}")
        
        # Print summary
        print("\n📊 ELIGIBLE DONOR SUMMARY:")
        
        # Blood type distribution
        print("\n🩸 Blood Type Distribution:")
        for bt in BLOOD_TYPES:
            bt_count = Donor.query.filter_by(blood_type=bt, is_eligible=True).count()
            if bt_count > 0:
                print(f"  {bt}: {bt_count}")
        
        # Availability
        available = Donor.query.filter_by(is_eligible=True, is_available=True).count()
        print(f"\n✅ Available for donation: {available}")
        print(f"⏸️  Not available: {created - available}")
        
        # Gender distribution
        print("\n👤 Gender Distribution:")
        for gender in GENDERS:
            gender_count = Donor.query.filter_by(gender=gender, is_eligible=True).count()
            if gender_count > 0:
                print(f"  {gender.title()}: {gender_count}")
        
        # City distribution
        print("\n🏙️ Top Cities:")
        from sqlalchemy import func
        city_stats = db.session.query(
            Donor.city, func.count(Donor.id)
        ).filter_by(is_eligible=True).group_by(Donor.city).order_by(func.count(Donor.id).desc()).limit(5).all()
        
        for city, count in city_stats:
            print(f"  {city}: {count}")
        
        print(f"\n🔍 You can now test features with these {created} eligible donors!")
        print("   • Donor passwords: Donor@123")
        print("   • Admin login: admin@blooddonor.com / Admin@123")

def add_eligible_donors_fast(count=1000):
    """Fast version - no donation history for speed"""
    app = create_app()
    
    with app.app_context():
        print("="*70)
        print(f"🩸 ADDING {count} ELIGIBLE DONORS (FAST MODE - NO DONATION HISTORY)")
        print("="*70)
        
        start_time = datetime.now()
        created = 0
        batch_size = 100
        
        for batch_start in range(0, count, batch_size):
            batch_end = min(batch_start + batch_size, count)
            
            for i in range(batch_start, batch_end):
                # Generate donor data
                first = random.choice(FIRST_NAMES)
                last = random.choice(LAST_NAMES)
                name = f"{first} {last}"
                email = random_email(first, last)
                phone = random_phone()
                
                city_data = random.choice(CITIES_STATES)
                age = random.randint(18, 55)
                birth_year = datetime.now().year - age
                birth_date = datetime(birth_year, random.randint(1, 12), random.randint(1, 28)).date()
                
                # Create user
                user = User(
                    email=email,
                    name=name,
                    phone=phone,
                    role='donor',
                    is_active=True,
                    created_at=random_date(2022, 2025)
                )
                user.set_password('Donor@123')
                db.session.add(user)
                db.session.flush()
                
                # Create eligible donor (no donation history)
                donor = Donor(
                    user_id=user.id,
                    blood_type=random.choice(BLOOD_TYPES),
                    date_of_birth=birth_date,
                    gender=random.choice(GENDERS),
                    weight=random.randint(50, 95),
                    address=random_address(),
                    city=city_data[0],
                    state=city_data[1],
                    pincode=random_pincode(),
                    latitude=city_data[2] + random.uniform(-0.3, 0.3),
                    longitude=city_data[3] + random.uniform(-0.3, 0.3),
                    is_available=random.choice([True, False]),
                    is_eligible=True,
                    total_donations=0,
                    emergency_contact_name=f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
                    emergency_contact_phone=random_phone(),
                    emergency_contact_relation=random.choice(['Spouse', 'Parent', 'Sibling']),
                    nationality='Indian',
                    has_disability=False,
                    profile_photo=None
                )
                db.session.add(donor)
                created += 1
            
            db.session.commit()
            print(f"✅ Added {batch_end}/{count} eligible donors...")
        
        elapsed = datetime.now() - start_time
        print(f"\n✅ Successfully added {created} eligible donors in {elapsed.total_seconds():.1f} seconds!")

if __name__ == "__main__":
    import sys
    
    # Choose mode
    print("Choose mode:")
    print("1. Full mode (with donation history) - slower but realistic")
    print("2. Fast mode (no donation history) - quick for testing")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == '2':
        add_eligible_donors_fast(1000)
    else:
        add_eligible_donors(1000)