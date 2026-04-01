# populate_database.py
"""
Complete Database Population Script
Run: python populate_database.py
This will create 5000+ donors, 100+ hospitals, and 1000+ blood requests
"""

import sys
import os
import random
import string
from datetime import datetime, timedelta
import time

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now import from app
from app import create_app, db
from app.models.user import User
from app.models.donor import Donor
from app.models.donation import Donation
from app.models.blood_request import BloodRequest
from app.models.hospital import Hospital

# ==================== SAMPLE DATA ====================

FIRST_NAMES = [
    'Raj', 'Priya', 'Amit', 'Sunita', 'Vikram', 'Neha', 'Rahul', 'Pooja', 'Sanjay', 'Anita',
    'Deepak', 'Kavita', 'Manoj', 'Rekha', 'Suresh', 'Meena', 'Ramesh', 'Geeta', 'Mahesh', 'Sneha',
    'Ashok', 'Nisha', 'Vijay', 'Shweta', 'Pankaj', 'Jyoti', 'Anil', 'Sarita', 'Nitin', 'Kiran',
    'Rajesh', 'Divya', 'Sunil', 'Anjali', 'Ajay', 'Ritu', 'Arun', 'Shilpa', 'Vivek', 'Pallavi',
    'Jatin', 'Monika', 'Gaurav', 'Shalini', 'Tarun', 'Richa', 'Naveen', 'Babita', 'Kunal', 'Sapna',
    'Mohit', 'Isha', 'Karan', 'Simran', 'Ravi', 'Ankita', 'Dinesh', 'Preeti', 'Hemant', 'Nidhi',
    'Yogesh', 'Swati', 'Praveen', 'Archana', 'Mukesh', 'Komal', 'Vinod', 'Seema', 'Pramod', 'Rani',
    'Umesh', 'Savita', 'Surendra', 'Kavya', 'Jitendra', 'Madhu', 'Gopal', 'Sudha', 'Lalit', 'Rekha',
    'Bhavesh', 'Hetal', 'Chintan', 'Krupa', 'Keyur', 'Dhara', 'Harsh', 'Mitali', 'Nirav', 'Bhavna'
]

LAST_NAMES = [
    'Sharma', 'Verma', 'Patel', 'Kumar', 'Singh', 'Gupta', 'Joshi', 'Malhotra', 'Reddy', 'Yadav',
    'Mehta', 'Choudhary', 'Mishra', 'Thakur', 'Saxena', 'Trivedi', 'Desai', 'Menon', 'Nair', 'Pillai',
    'Rao', 'Naidu', 'Prasad', 'Sinha', 'Das', 'Ghosh', 'Banerjee', 'Chatterjee', 'Mukherjee', 'Bose',
    'Khan', 'Ansari', 'Sheikh', 'Begum', 'Ahmad', 'Ali', 'Hussain', 'Iqbal', 'Rahman', 'Malik',
    'Kaur', 'Dhillon', 'Brar', 'Gill', 'Sandhu', 'Sidhu', 'Ahluwalia', 'Chadha', 'Khanna', 'Kapoor'
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
    ('Nagpur', 'Maharashtra', 21.1458, 79.0882),
    ('Indore', 'Madhya Pradesh', 22.7196, 75.8577),
    ('Bhopal', 'Madhya Pradesh', 23.2599, 77.4126),
    ('Visakhapatnam', 'Andhra Pradesh', 17.6868, 83.2185),
    ('Patna', 'Bihar', 25.5941, 85.1376),
    ('Vadodara', 'Gujarat', 22.3072, 73.1812),
    ('Surat', 'Gujarat', 21.1702, 72.8311),
    ('Coimbatore', 'Tamil Nadu', 11.0168, 76.9558),
    ('Mysore', 'Karnataka', 12.2958, 76.6394),
    ('Chandigarh', 'Chandigarh', 30.7333, 76.7794)
]

BLOOD_TYPES = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
GENDERS = ['male', 'female', 'other']
URGENCY_LEVELS = ['low', 'medium', 'high', 'emergency']
REQUEST_STATUS = ['pending', 'fulfilled', 'cancelled', 'expired']

HOSPITAL_NAMES = [
    'City General Hospital', 'Apollo Hospital', 'Fortis Hospital', 'Max Hospital', 'AIIMS',
    'Medanta Hospital', 'Christian Medical College', 'Narayana Health', 'Manipal Hospital',
    'Kokilaben Hospital', 'Lilavati Hospital', 'Jaslok Hospital', 'Breach Candy Hospital',
    'Ruby Hall Clinic', 'Jehangir Hospital', 'KEM Hospital', 'Sion Hospital', 'LTMG Hospital',
    'Tata Memorial Hospital', 'Hinduja Hospital', 'Wockhardt Hospital', 'Columbia Asia Hospital',
    'Global Hospital', 'Seven Hills Hospital', 'Apollo Spectra', 'Nova IVF Fertility'
]

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

# ==================== MAIN POPULATION FUNCTIONS ====================

def create_hospitals(count=50):
    """Create sample hospitals"""
    print(f"\n🏥 Creating {count} hospitals...")
    hospitals = []
    
    for i in range(count):
        city_data = random.choice(CITIES_STATES)
        name = f"{random.choice(HOSPITAL_NAMES)} {random.choice(['', 'Main', 'Central', 'North', 'South', 'East', 'West'])}"
        
        # Generate coordinates near the city
        lat = city_data[2] + random.uniform(-0.1, 0.1)
        lon = city_data[3] + random.uniform(-0.1, 0.1)
        
        hospital = Hospital(
            name=name.strip(),
            phone=random_phone(),
            email=random_email(name.split()[0], name.split()[-1]),
            emergency_phone=random_phone(),
            address=random_address(),
            city=city_data[0],
            state=city_data[1],
            pincode=random_pincode(),
            latitude=lat,
            longitude=lon,
            hospital_type=random.choice(['Government', 'Private', 'Trust']),
            has_blood_bank=random.choice([True, False]),
            is_verified=random.choice([True, False]),
            contact_person_name=f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
            contact_person_phone=random_phone(),
            contact_person_designation=random.choice(['Administrator', 'Manager', 'Director', 'Coordinator']),
            created_at=random_date(2020, 2025)
        )
        db.session.add(hospital)
        hospitals.append(hospital)
        
        if (i + 1) % 10 == 0:
            db.session.commit()
            print(f"  ✅ {i + 1} hospitals created...")
    
    db.session.commit()
    print(f"✅ Created {len(hospitals)} hospitals")
    return hospitals

def create_donors(count=5000):
    """Create sample donors"""
    print(f"\n🩸 Creating {count} donors...")
    donors = []
    start_time = time.time()
    
    # Progress tracking
    batch_size = 100
    for batch_start in range(0, count, batch_size):
        batch_end = min(batch_start + batch_size, count)
        
        for i in range(batch_start, batch_end):
            first = random.choice(FIRST_NAMES)
            last = random.choice(LAST_NAMES)
            name = f"{first} {last}"
            email = random_email(first, last)
            phone = random_phone()
            
            # Random city
            city_data = random.choice(CITIES_STATES)
            
            # Generate age between 18 and 65
            age = random.randint(18, 65)
            birth_year = datetime.now().year - age
            birth_date = datetime(birth_year, random.randint(1, 12), random.randint(1, 28)).date()
            
            # Create user
            user = User(
                email=email,
                name=name,
                phone=phone,
                role='donor',
                is_active=random.choice([True, True, True, False]),  # 75% active
                created_at=random_date(2020, 2025)
            )
            user.set_password('Donor@123')
            db.session.add(user)
            db.session.flush()
            
            # Generate random coordinates near city
            lat = city_data[2] + random.uniform(-0.5, 0.5)
            lon = city_data[3] + random.uniform(-0.5, 0.5)
            
            # Determine eligibility based on various factors
            is_eligible = random.choice([True, False])
            is_available = random.choice([True, False])
            
            # Some donors are not eligible due to recent donation
            last_donation_date = None
            total_donations = random.randint(0, 20)
            
            if total_donations > 0 and random.choice([True, False]):
                last_donation_date = random_date(2023, 2025)
                # If donated within last 90 days, not eligible
                if last_donation_date and (datetime.now() - last_donation_date).days < 90:
                    is_eligible = False
            
            # Create donor profile
            donor = Donor(
                user_id=user.id,
                blood_type=random.choice(BLOOD_TYPES),
                date_of_birth=birth_date,
                gender=random.choice(GENDERS),
                weight=random.randint(45, 100),
                address=random_address(),
                city=city_data[0],
                state=city_data[1],
                pincode=random_pincode(),
                latitude=lat,
                longitude=lon,
                location_updated_at=datetime.utcnow(),
                medical_conditions=random.choice(['None', 'Diabetes', 'Hypertension', 'Asthma', None]),
                medications=random.choice(['None', 'Blood pressure medication', 'Insulin', None]),
                last_donation_date=last_donation_date,
                total_donations=total_donations,
                is_available=is_available,
                is_eligible=is_eligible,
                emergency_contact_name=f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
                emergency_contact_phone=random_phone(),
                emergency_contact_relation=random.choice(['Spouse', 'Parent', 'Sibling', 'Friend', 'Child']),
                nationality=random.choice(['Indian', 'Indian', 'Indian', 'Other']),
                has_disability=random.choice([True, False, False, False]),  # 25% have disability
                disability=random.choice(['None', 'Visual impairment', 'Hearing impairment', 'Physical disability', None]),
                profile_photo=None,
                #profile_photo_url=None,
                created_at=user.created_at
            )
            db.session.add(donor)
            donors.append(donor)
            
            # Create donation records for donors with donations
            if total_donations > 0:
                donation_count = min(total_donations, 10)  # Limit to 10 donations
                for d in range(donation_count):
                    donation_date = random_date(2023, 2025)
                    donation = Donation(
                    donor_id=user.id,
                    donor_name=user.name,
                    donor_blood_type=donor.blood_type,
                    donation_date=donation_date,
                    units_donated=random.randint(1, 2),
                    donation_center=random.choice(DONATION_CENTERS),
                    is_verified=random.choice([True, False]),
                    certificate_generated=random.choice([True, False]),
                    blood_pressure=f"{random.randint(110, 130)}/{random.randint(70, 90)}",
                    hemoglobin_level=round(random.uniform(12.0, 16.0), 1)
                    )
                    db.session.add(donation)
        
        # Commit batch
        db.session.commit()
        
        # Progress report
        elapsed = time.time() - start_time
        rate = batch_end / elapsed if elapsed > 0 else 0
        print(f"  ✅ Created {batch_end}/{count} donors... ({rate:.1f} donors/sec)")
    
    print(f"✅ Created {len(donors)} donors in {time.time() - start_time:.1f} seconds")
    return donors

def create_blood_requests(donors, hospitals, count=1000):
    """Create sample blood requests"""
    print(f"\n📋 Creating {count} blood requests...")
    requests = []
    
    for i in range(count):
        donor = random.choice(donors)
        hospital = random.choice(hospitals) if hospitals else None
        urgency = random.choice(URGENCY_LEVELS)
        status = random.choice(REQUEST_STATUS)
        
        # Calculate expiry based on urgency
        created_at = random_date(2024, 2025)
        if urgency == 'emergency':
            expires_at = created_at + timedelta(hours=48)
        else:
            expires_at = created_at + timedelta(days=random.randint(3, 10))
        
        # Determine if fulfilled
        fulfilled_at = None
        if status == 'fulfilled':
            fulfilled_at = created_at + timedelta(hours=random.randint(1, 48))
        
        blood_request = BloodRequest(
            requester_id=donor.user_id,
            requester_name=donor.user.name,
            requester_phone=donor.user.phone,
            requester_email=donor.user.email,
            requester_type=random.choice(['patient', 'relative', 'hospital']),
            patient_name=f"Patient {random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
            patient_age=random.randint(1, 85),
            patient_gender=random.choice(GENDERS),
            blood_type_needed=random.choice(BLOOD_TYPES),
            units_needed=random.randint(1, 4),
            hospital_name=hospital.name if hospital else None,
            hospital_address=hospital.address if hospital else None,
            hospital_latitude=hospital.latitude if hospital else donor.latitude,
            hospital_longitude=hospital.longitude if hospital else donor.longitude,
            urgency=urgency,
            status=status,
            reason=random.choice(['Accident', 'Surgery', 'Childbirth', 'Thalassemia', 'Cancer treatment', None]),
            required_by_date=created_at.date() + timedelta(days=random.randint(1, 7)),
            requester_latitude=donor.latitude,
            requester_longitude=donor.longitude,
            search_radius=random.choice([5, 10, 20, 50]),
            notified_donors=random.randint(0, 20),
            accepted_donors=random.randint(0, 3),
            created_at=created_at,
            expires_at=expires_at,
            fulfilled_at=fulfilled_at
        )
        db.session.add(blood_request)
        requests.append(blood_request)
        
        if (i + 1) % 100 == 0:
            db.session.commit()
            print(f"  ✅ Created {i + 1} blood requests...")
    
    db.session.commit()
    print(f"✅ Created {len(requests)} blood requests")
    return requests

def create_admin_user():
    """Create admin user if not exists"""
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        admin = User(
            email='admin@blooddonor.com',
            name='System Administrator',
            phone='9999999999',
            role='admin',
            is_active=True,
            created_at=datetime.utcnow()
        )
        admin.set_password('Admin@123')
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin user created")
    else:
        print("✅ Admin user already exists")
    return admin

def print_statistics():
    """Print database statistics"""
    print("\n" + "="*60)
    print("📊 DATABASE STATISTICS")
    print("="*60)
    
    print(f"\n👥 Users: {User.query.count():,}")
    print(f"🩸 Donors: {Donor.query.count():,}")
    print(f"🏥 Hospitals: {Hospital.query.count():,}")
    print(f"📋 Blood Requests: {BloodRequest.query.count():,}")
    print(f"🎁 Donations: {Donation.query.count():,}")
    print(f"📝 Admin Logs: {AdminLog.query.count():,}")
    
    # Blood type distribution
    print("\n🩸 Blood Type Distribution:")
    for bt in BLOOD_TYPES:
        count = Donor.query.filter_by(blood_type=bt).count()
        percentage = (count / Donor.query.count() * 100) if Donor.query.count() > 0 else 0
        print(f"  {bt}: {count:,} ({percentage:.1f}%)")
    
    # Gender distribution
    print("\n👤 Gender Distribution:")
    for gender in GENDERS:
        count = Donor.query.filter_by(gender=gender).count()
        percentage = (count / Donor.query.count() * 100) if Donor.query.count() > 0 else 0
        print(f"  {gender.title()}: {count:,} ({percentage:.1f}%)")
    
    # City distribution
    print("\n🏙️ Top 10 Cities:")
    city_counts = db.session.query(Donor.city, db.func.count(Donor.id)).group_by(Donor.city).order_by(db.func.count(Donor.id).desc()).limit(10).all()
    for city, count in city_counts:
        print(f"  {city}: {count:,}")
    
    # Request status
    print("\n📊 Request Status:")
    for status in ['pending', 'fulfilled', 'cancelled', 'expired']:
        count = BloodRequest.query.filter_by(status=status).count()
        print(f"  {status.title()}: {count:,}")
    
    # Urgency levels
    print("\n🚨 Request Urgency:")
    for urgency in URGENCY_LEVELS:
        count = BloodRequest.query.filter_by(urgency=urgency).count()
        print(f"  {urgency.title()}: {count:,}")
    
    # Eligibility
    eligible = Donor.query.filter_by(is_eligible=True).count()
    available = Donor.query.filter_by(is_available=True).count()
    print(f"\n✅ Eligible Donors: {eligible:,}")
    print(f"📱 Available Donors: {available:,}")

# ==================== MAIN FUNCTION ====================

def main():
    """Main function to populate database"""
    print("="*70)
    print("🚀 DATABASE POPULATION SCRIPT")
    print("="*70)
    print("\nThis script will create:")
    print("  • 5,000+ blood donors")
    print("  • 50+ hospitals")
    print("  • 1,000+ blood requests")
    print("  • Donation records")
    print("  • Admin user")
    
    # Confirm
    print("\n⚠️  This will clear existing data!")
    response = input("\nDo you want to continue? (yes/no): ")
    if response.lower() != 'yes':
        print("❌ Operation cancelled")
        return
    
    app = create_app()
    with app.app_context():
        # Clear existing data
        print("\n🗑️  Clearing existing data...")
        db.session.query(Donation).delete()
        db.session.query(BloodRequest).delete()
        db.session.query(Donor).delete()
        db.session.query(User).delete()
        db.session.query(Hospital).delete()
        db.session.commit()
        print("✅ Database cleared")
        
        # Create data
        start_total = time.time()
        
        # Create admin
        admin = create_admin_user()
        
        # Create hospitals
        hospitals = create_hospitals(50)
        
        # Create donors
        donors = create_donors(5000)
        
        # Create blood requests
        requests = create_blood_requests(donors, hospitals, 1000)
        
        # Final commit
        db.session.commit()
        
        # Print statistics
        print_statistics()
        
        total_time = time.time() - start_total
        print(f"\n⏱️  Total time: {total_time:.2f} seconds")
        
        print("\n" + "="*70)
        print("✅ DATABASE POPULATION COMPLETE!")
        print("="*70)
        print("\n📝 Test Credentials:")
        print("  • Admin: admin@blooddonor.com / Admin@123")
        print("  • Donors: [any donor email] / Donor@123")
        print("\n🔗 Test these features:")
        print("  • Donor Dashboard: http://127.0.0.1:5000/donor/dashboard")
        print("  • Admin Dashboard: http://127.0.0.1:5000/admin/dashboard")
        print("  • Nearby Donors: http://127.0.0.1:5000/donor/nearby-donors")
        print("  • Nearby Hospitals: http://127.0.0.1:5000/donor/nearby-hospitals")
        print("  • Emergency Search: http://127.0.0.1:5000/donor/emergency-search")

if __name__ == "__main__":
    main()