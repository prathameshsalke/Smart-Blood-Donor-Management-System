#!/usr/bin/env python
"""
Complete Database Population Script
====================================
This script populates the database with:
- 5,000+ donors (with 2,000+ eligible)
- 5,000+ hospitals
- 5 admin users
- Blood requests and donations

Run: python scripts/populate_complete_db.py
"""

import sys
import os
import random
import uuid
import hashlib
from datetime import datetime, timedelta
import time
from faker import Faker
from werkzeug.security import generate_password_hash

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.user import User
from app.models.donor import Donor
from app.models.hospital import Hospital
from app.models.blood_request import BloodRequest
from app.models.donation import Donation
from app.models.admin_log import AdminLog

# Initialize Faker for realistic Indian data
fake = Faker('en_IN')

# ==================== CONSTANTS ====================

BLOOD_TYPES = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
GENDERS = ['male', 'female', 'other']
URGENCY_LEVELS = ['low', 'medium', 'high', 'emergency']
REQUEST_STATUS = ['pending', 'fulfilled', 'cancelled', 'expired']

# Indian states and major cities with coordinates
LOCATIONS = [
    # State, City, Latitude, Longitude, Population Factor
    ('Maharashtra', 'Mumbai', 19.0760, 72.8777, 1.5),
    ('Maharashtra', 'Pune', 18.5204, 73.8567, 1.2),
    ('Maharashtra', 'Nagpur', 21.1458, 79.0882, 1.0),
    ('Delhi', 'Delhi', 28.6139, 77.2090, 1.4),
    ('Karnataka', 'Bangalore', 12.9716, 77.5946, 1.3),
    ('Karnataka', 'Mysore', 12.2958, 76.6394, 0.9),
    ('Tamil Nadu', 'Chennai', 13.0827, 80.2707, 1.2),
    ('Tamil Nadu', 'Coimbatore', 11.0168, 76.9558, 1.0),
    ('Telangana', 'Hyderabad', 17.3850, 78.4867, 1.2),
    ('West Bengal', 'Kolkata', 22.5726, 88.3639, 1.1),
    ('Gujarat', 'Ahmedabad', 23.0225, 72.5714, 1.1),
    ('Gujarat', 'Surat', 21.1702, 72.8311, 1.0),
    ('Rajasthan', 'Jaipur', 26.9124, 75.7873, 1.0),
    ('Uttar Pradesh', 'Lucknow', 26.8467, 80.9462, 1.0),
    ('Uttar Pradesh', 'Kanpur', 26.4499, 80.3319, 0.9),
    ('Bihar', 'Patna', 25.5941, 85.1376, 0.9),
    ('Madhya Pradesh', 'Bhopal', 23.2599, 77.4126, 0.9),
    ('Madhya Pradesh', 'Indore', 22.7196, 75.8577, 1.0),
    ('Punjab', 'Ludhiana', 30.9000, 75.8500, 0.9),
    ('Haryana', 'Gurgaon', 28.4595, 77.0266, 1.1),
    ('Kerala', 'Thiruvananthapuram', 8.5241, 76.9366, 0.9),
    ('Odisha', 'Bhubaneswar', 20.2961, 85.8245, 0.9),
]

# Hospital name components
HOSPITAL_PREFIXES = ['City', 'District', 'General', 'Government', 'Private', 'Super', 'Metro', 'Central', 'National', 'International']
HOSPITAL_TYPES = ['Hospital', 'Medical Center', 'Healthcare', 'Nursing Home', 'Clinic', 'Institute', 'Trust']
HOSPITAL_SUFFIXES = ['Ltd', 'Pvt Ltd', 'Trust', 'Foundation', 'Society', 'Group']

# Indian names for donors
INDIAN_FIRST_NAMES = [
    'Aarav', 'Vihaan', 'Vivaan', 'Ananya', 'Diya', 'Advik', 'Kabir', 'Anaya', 'Ayaan', 'Reyansh',
    'Sai', 'Arjun', 'Ishaan', 'Shaurya', 'Aadhya', 'Anvi', 'Prisha', 'Rudra', 'Samaira', 'Pari',
    'Yash', 'Aaradhya', 'Sia', 'Myra', 'Aryan', 'Krishna', 'Laksh', 'Ved', 'Dhruv', 'Rohan',
    'Simran', 'Kavya', 'Riya', 'Jhanvi', 'Ishita', 'Anjali', 'Priya', 'Neha', 'Pooja', 'Sneha',
    'Raj', 'Amit', 'Sunil', 'Sanjay', 'Vikram', 'Rahul', 'Deepak', 'Manoj', 'Suresh', 'Ramesh',
    'Priyanka', 'Divya', 'Shreya', 'Nikita', 'Komal', 'Richa', 'Nidhi', 'Swati', 'Pallavi', 'Madhuri'
]

INDIAN_LAST_NAMES = [
    'Sharma', 'Verma', 'Gupta', 'Kumar', 'Singh', 'Patel', 'Reddy', 'Yadav', 'Jha', 'Thakur',
    'Mishra', 'Prasad', 'Choudhary', 'Malhotra', 'Mehta', 'Joshi', 'Desai', 'Menon', 'Nair', 'Pillai',
    'Rao', 'Naidu', 'Das', 'Ghosh', 'Banerjee', 'Chatterjee', 'Mukherjee', 'Bose', 'Sen', 'Pal',
    'Khan', 'Ansari', 'Sheikh', 'Begum', 'Ahmad', 'Ali', 'Hussain', 'Iqbal', 'Rahman', 'Malik',
    'Kaur', 'Dhillon', 'Brar', 'Gill', 'Sandhu', 'Sidhu', 'Ahluwalia', 'Chadha', 'Khanna', 'Kapoor'
]

# ==================== HELPER FUNCTIONS ====================

class ProgressBar:
    """Simple progress bar for console output"""
    def __init__(self, total, prefix='', suffix='', length=50, fill='█'):
        self.total = total
        self.prefix = prefix
        self.suffix = suffix
        self.length = length
        self.fill = fill
        self.start_time = time.time()
    
    def update(self, iteration):
        percent = (iteration / self.total)
        filled_length = int(self.length * percent)
        bar = self.fill * filled_length + '-' * (self.length - filled_length)
        elapsed = time.time() - self.start_time
        if iteration > 0:
            eta = elapsed * (self.total / iteration - 1)
            eta_str = f"ETA: {eta:.1f}s"
        else:
            eta_str = "ETA: --"
        print(f'\r{self.prefix} |{bar}| {percent:.1%} {self.suffix} [{iteration}/{self.total}] {eta_str}', end='\r')
        if iteration == self.total:
            print()

def random_date(start_year=1970, end_year=2005):
    """Generate random date"""
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    return start + timedelta(days=random.randint(0, (end - start).days))

def random_phone():
    """Generate random Indian phone number"""
    return f"{random.choice([6,7,8,9])}{random.randint(100000000, 999999999)}"

def random_email(name):
    """Generate random email"""
    domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'rediffmail.com', 'gmail.co.in']
    name_clean = name.lower().replace(' ', '.')
    number = random.randint(1, 999)
    return f"{name_clean}{number}@{random.choice(domains)}"

def random_address():
    """Generate random Indian address"""
    street_names = ['Main Road', 'MG Road', 'Park Street', 'Church Street', 'Commercial Street', 
                   'Residency Road', 'Cunningham Road', 'Brigade Road', 'Linking Road', 'Marine Drive']
    return f"{random.randint(1, 999)}, {random.choice(street_names)}"

def random_pincode():
    """Generate random 6-digit pincode"""
    return f"{random.randint(100000, 999999)}"

def generate_donor_unique_id():
    """Generate unique donor ID"""
    timestamp = datetime.now().strftime('%y%m%d%H%M%S')
    random_str = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=6))
    return f"D{timestamp}{random_str}"

def generate_hospital_unique_id():
    """Generate unique hospital ID"""
    timestamp = datetime.now().strftime('%y%m%d')
    random_str = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=8))
    return f"H{timestamp}{random_str}"

def calculate_age(dob):
    """Calculate age from date of birth"""
    today = datetime.now().date()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

# ==================== DATA GENERATION FUNCTIONS ====================

def create_admins(count=5):
    """Create admin users"""
    print(f"\n👑 Creating {count} admin users...")
    admins = []
    
    admin_data = [
        {'name': 'System Administrator', 'email': 'admin@blooddonor.com', 'role': 'super_admin'},
        {'name': 'Blood Bank Manager', 'email': 'manager@blooddonor.com', 'role': 'admin'},
        {'name': 'Hospital Coordinator', 'email': 'coordinator@blooddonor.com', 'role': 'admin'},
        {'name': 'Donor Relations Head', 'email': 'relations@blooddonor.com', 'role': 'admin'},
        {'name': 'Emergency Services Admin', 'email': 'emergency@blooddonor.com', 'role': 'emergency_admin'}
    ]
    
    for i in range(min(count, len(admin_data))):
        data = admin_data[i]
        user = User(
            email=data['email'],
            name=data['name'],
            phone=random_phone(),
            role='admin',
            is_active=True,
            created_at=datetime.now() - timedelta(days=random.randint(30, 365))
        )
        user.set_password('Admin@123')
        db.session.add(user)
        db.session.flush()
        
        # Create admin log entry
        log = AdminLog(
            admin_id=user.id,
            admin_email=user.email,
            action='CREATE',
            entity_type='ADMIN',
            description=f'Admin user {user.name} created',
            ip_address='127.0.0.1',
            created_at=user.created_at
        )
        db.session.add(log)
        admins.append(user)
    
    db.session.commit()
    print(f"✅ Created {len(admins)} admin users")
    return admins

# def create_hospitals(count=5000):
#     """Create hospital records"""
#     print(f"\n🏥 Creating {count} hospitals...")
#     hospitals = []
#     progress = ProgressBar(count, prefix='Progress:', suffix='Complete', length=50)
    
#     # Create hospitals distributed across locations
#     for i in range(count):
#         # Select location based on population factor
#         location = random.choices(LOCATIONS, weights=[l[4] for l in LOCATIONS])[0]
#         state, city, base_lat, base_lon, _ = location
        
#         # Generate hospital name
#         name_prefix = random.choice(HOSPITAL_PREFIXES)
#         name_type = random.choice(HOSPITAL_TYPES)
#         name_suffix = random.choice([''] + HOSPITAL_SUFFIXES)
#         hospital_name = f"{name_prefix} {city} {name_type} {name_suffix}".strip()
        
#         # Generate coordinates within city area (with variation)
#         lat = base_lat + random.uniform(-0.1, 0.1)
#         lon = base_lon + random.uniform(-0.1, 0.1)
        
#         # Create hospital
#         hospital = Hospital(
#             hospital_id=generate_hospital_unique_id(),
#             name=hospital_name,
#             phone=random_phone(),
#             email=random_email(hospital_name),
#             emergency_phone=random_phone(),
#             website=f"www.{hospital_name.lower().replace(' ', '')}.com",
#             address=random_address(),
#             city=city,
#             state=state,
#             pincode=random_pincode(),
#             latitude=lat,
#             longitude=lon,
#             hospital_type=random.choice(['Government', 'Private', 'Trust', 'Charity']),
#             has_blood_bank=random.choice([True, False]),
#             is_verified=random.choice([True, False, True]),  # 2/3 chance of being verified
#             contact_person_name=f"{random.choice(INDIAN_FIRST_NAMES)} {random.choice(INDIAN_LAST_NAMES)}",
#             contact_person_phone=random_phone(),
#             contact_person_designation=random.choice(['Administrator', 'Medical Director', 'HR Manager', 'Blood Bank Incharge']),
#             registration_number=f"REG{random.randint(10000, 99999)}",
#             license_number=f"LIC{random.randint(10000, 99999)}",
#             created_at=random_date(2010, 2025)
#         )
#         db.session.add(hospital)
#         hospitals.append(hospital)
        
#         if (i + 1) % 100 == 0:
#             db.session.flush()
        
#         progress.update(i + 1)
    
#     db.session.commit()
#     print(f"✅ Created {len(hospitals)} hospitals")
#     return hospitals

def create_hospitals(count=5000):
    """Create hospital records with guaranteed unique registration numbers"""
    print(f"\n🏥 Creating {count} hospitals...")
    hospitals = []
    progress = ProgressBar(count, prefix='Progress:', suffix='Complete', length=50)
    
    # Track used registration numbers to avoid duplicates
    used_reg_numbers = set()
    used_license_numbers = set()
    used_hospital_ids = set()
    
    for i in range(count):
        # Select location based on population factor
        location = random.choices(LOCATIONS, weights=[l[4] for l in LOCATIONS])[0]
        state, city, base_lat, base_lon, _ = location
        
        # Generate hospital name
        name_prefix = random.choice(HOSPITAL_PREFIXES)
        name_type = random.choice(HOSPITAL_TYPES)
        name_suffix = random.choice([''] + HOSPITAL_SUFFIXES)
        hospital_name = f"{name_prefix} {city} {name_type} {name_suffix}".strip()
        
        # Generate unique registration number
        while True:
            reg_num = f"REG{random.randint(10000, 99999)}"
            if reg_num not in used_reg_numbers:
                used_reg_numbers.add(reg_num)
                break
        
        # Generate unique license number
        while True:
            license_num = f"LIC{random.randint(10000, 99999)}"
            if license_num not in used_license_numbers:
                used_license_numbers.add(license_num)
                break
        
        # Generate unique hospital ID
        while True:
            hospital_id = generate_hospital_unique_id()
            if hospital_id not in used_hospital_ids:
                used_hospital_ids.add(hospital_id)
                break
        
        # Generate coordinates within city area (with variation)
        lat = base_lat + random.uniform(-0.1, 0.1)
        lon = base_lon + random.uniform(-0.1, 0.1)
        
        # Create hospital
        hospital = Hospital(
            hospital_id=hospital_id,
            name=hospital_name,
            phone=random_phone(),
            email=random_email(hospital_name),
            emergency_phone=random_phone(),
            website=f"www.{hospital_name.lower().replace(' ', '')}.com",
            address=random_address(),
            city=city,
            state=state,
            pincode=random_pincode(),
            latitude=lat,
            longitude=lon,
            hospital_type=random.choice(['Government', 'Private', 'Trust', 'Charity']),
            has_blood_bank=random.choice([True, False]),
            is_verified=random.choice([True, False, True]),  # 2/3 chance of being verified
            contact_person_name=f"{random.choice(INDIAN_FIRST_NAMES)} {random.choice(INDIAN_LAST_NAMES)}",
            contact_person_phone=random_phone(),
            contact_person_designation=random.choice(['Administrator', 'Medical Director', 'HR Manager', 'Blood Bank Incharge']),
            registration_number=reg_num,
            license_number=license_num,
            created_at=random_date(2010, 2025)
        )
        db.session.add(hospital)
        hospitals.append(hospital)
        
        if (i + 1) % 100 == 0:
            db.session.flush()
        
        progress.update(i + 1)
    
    db.session.commit()
    print(f"✅ Created {len(hospitals)} hospitals")
    return hospitals

# def create_donors(count=5000, eligible_target=2000):
#     """Create donor records with specified eligible count"""
#     print(f"\n🩸 Creating {count} donors (target: {eligible_target}+ eligible)...")
#     donors = []
#     progress = ProgressBar(count, prefix='Progress:', suffix='Complete', length=50)
    
#     eligible_count = 0
#     batch_size = 100
    
#     for i in range(count):
#         # Generate basic info
#         first_name = random.choice(INDIAN_FIRST_NAMES)
#         last_name = random.choice(INDIAN_LAST_NAMES)
#         name = f"{first_name} {last_name}"
#         email = random_email(name)
#         phone = random_phone()
        
#         # Select location
#         location = random.choices(LOCATIONS, weights=[l[4] for l in LOCATIONS])[0]
#         state, city, base_lat, base_lon, _ = location
        
#         # Generate age between 18 and 65
#         age = random.randint(18, 65)
#         birth_year = datetime.now().year - age
#         birth_month = random.randint(1, 12)
#         birth_day = random.randint(1, 28)
#         dob = datetime(birth_year, birth_month, birth_day).date()
        
#         # Create user
#         user = User(
#             email=email,
#             name=name,
#             phone=phone,
#             role='donor',
#             is_active=True,
#             created_at=random_date(2018, 2025)
#         )
#         user.set_password('Donor@123')
#         db.session.add(user)
#         db.session.flush()
        
#         # Generate location coordinates
#         lat = base_lat + random.uniform(-0.3, 0.3)
#         lon = base_lon + random.uniform(-0.3, 0.3)
        
#         # Determine eligibility (target 2000+ eligible)
#         # Make eligible if we haven't reached target OR randomly for others
#         if eligible_count < eligible_target:
#             make_eligible = True
#         else:
#             make_eligible = random.random() < 0.3  # 30% chance after target
        
#         # Generate donation history
#         total_donations = 0
#         last_donation_date = None
#         days_since_last = 999
        
#         if make_eligible:
#             # Eligible donors can have donation history > 90 days ago
#             total_donations = random.randint(1, 15)
#             if total_donations > 0 and random.random() < 0.8:
#                 days_ago = random.randint(100, 365)  # > 90 days
#                 last_donation_date = datetime.now() - timedelta(days=days_ago)
#                 days_since_last = days_ago
#                 eligible_count += 1
#         else:
#             # Non-eligible donors might have recent donation or other issues
#             total_donations = random.randint(0, 8)
#             if total_donations > 0 and random.random() < 0.7:
#                 days_ago = random.randint(1, 89)  # < 90 days
#                 last_donation_date = datetime.now() - timedelta(days=days_ago)
#                 days_since_last = days_ago
        
#         # Create donor profile
#         donor = Donor(
#             donor_unique_id=generate_donor_unique_id(),
#             user_id=user.id,
#             blood_type=random.choice(BLOOD_TYPES),
#             date_of_birth=dob,
#             gender=random.choice(GENDERS),
#             weight=random.randint(45, 100),
#             nationality=random.choice(['Indian', 'Indian', 'Indian', 'Other']),
#             has_disability=random.choice([False, False, False, True]),  # 25% have disability
#             disability=random.choice([None, None, None, 'Mobility impairment', 'Visual impairment', 'Hearing impairment']),
#             address=random_address(),
#             city=city,
#             state=state,
#             pincode=random_pincode(),
#             latitude=lat,
#             longitude=lon,
#             location_updated_at=datetime.now() - timedelta(days=random.randint(0, 30)),
#             medical_conditions=random.choice([None, None, 'Mild Asthma', 'Controlled BP', 'Diabetes Type 2']),
#             medications=random.choice([None, None, 'Blood pressure medication', 'Insulin']),
#             last_donation_date=last_donation_date,
#             total_donations=total_donations,
#             is_available=random.choice([True, False]),
#             is_eligible=make_eligible,
#             emergency_contact_name=f"{random.choice(INDIAN_FIRST_NAMES)} {random.choice(INDIAN_LAST_NAMES)}",
#             emergency_contact_phone=random_phone(),
#             emergency_contact_relation=random.choice(['Spouse', 'Parent', 'Sibling', 'Friend', 'Child']),
#             created_at=user.created_at
#         )
#         db.session.add(donor)
#         donors.append(donor)
        
#         # Create donation records for donors with history
#         if total_donations > 0:
#             donation_count = min(total_donations, 5)  # Limit to 5 for performance
#             donation_dates = []
            
#             # Generate spread out donation dates
#             for d in range(donation_count):
#                 if d == 0 and last_donation_date:
#                     donation_date = last_donation_date
#                 else:
#                     days_offset = random.randint(200, 800)
#                     donation_date = (last_donation_date or datetime.now()) - timedelta(days=days_offset)
#                 donation_dates.append(donation_date)
            
#             donation_dates.sort()
            
#             for donation_date in donation_dates:
#                 donation = Donation(
#                     donor_id=user.id,
#                     donor_name=user.name,
#                     donor_blood_type=donor.blood_type,
#                     donation_date=donation_date,
#                     units_donated=random.randint(1, 2),
#                     donation_center=random.choice(['Red Cross Camp', 'City Hospital', 'Blood Bank', 'Mobile Camp']),
#                     is_verified=random.choice([True, True, False]),
#                     certificate_generated=random.choice([True, True, False]),
#                     blood_pressure=f"{random.randint(110, 130)}/{random.randint(70, 90)}",
#                     hemoglobin_level=round(random.uniform(12.0, 16.0), 1)
#                 )
#                 # Generate unique donation ID
#                 donation.donation_id = f"DON{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:6].upper()}"
#                 db.session.add(donation)
        
#         # Commit in batches
#         if (i + 1) % batch_size == 0:
#             db.session.flush()
        
#         progress.update(i + 1)
    
#     db.session.commit()
#     print(f"\n✅ Created {len(donors)} donors")
#     print(f"   Eligible donors: {eligible_count} (target: {eligible_target}+)")
#     return donors


def create_donors(count=5000, eligible_target=2000):
    """Create donor records with guaranteed unique emails"""
    print(f"\n🩸 Creating {count} donors (target: {eligible_target}+ eligible)...")
    donors = []
    progress = ProgressBar(count, prefix='Progress:', suffix='Complete', length=50)
    
    eligible_count = 0
    batch_size = 100
    
    # Track used emails to avoid duplicates
    used_emails = set()
    used_phones = set()
    used_donor_ids = set()
    
    for i in range(count):
        # Generate unique email
        while True:
            first_name = random.choice(INDIAN_FIRST_NAMES)
            last_name = random.choice(INDIAN_LAST_NAMES)
            name = f"{first_name} {last_name}"
            
            # More robust unique email generation
            base_email = f"{first_name.lower()}.{last_name.lower()}"
            # Add timestamp component for guaranteed uniqueness
            timestamp = datetime.now().strftime('%H%M%S%f')[-6:]
            email = f"{base_email}{timestamp}{random.randint(1, 9999)}@{random.choice(['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com'])}"
            
            if email not in used_emails:
                used_emails.add(email)
                break
        
        # Generate unique phone
        while True:
            phone = random_phone()
            if phone not in used_phones:
                used_phones.add(phone)
                break
        
        # Generate unique donor ID
        while True:
            donor_unique_id = generate_donor_unique_id()
            if donor_unique_id not in used_donor_ids:
                used_donor_ids.add(donor_unique_id)
                break
        
        # Select location
        location = random.choices(LOCATIONS, weights=[l[4] for l in LOCATIONS])[0]
        state, city, base_lat, base_lon, _ = location
        
        # Generate age between 18 and 65
        age = random.randint(18, 65)
        birth_year = datetime.now().year - age
        birth_month = random.randint(1, 12)
        birth_day = random.randint(1, 28)
        dob = datetime(birth_year, birth_month, birth_day).date()
        
        # Create user
        user = User(
            email=email,
            name=name,
            phone=phone,
            role='donor',
            is_active=True,
            created_at=random_date(2018, 2025)
        )
        user.set_password('Donor@123')
        db.session.add(user)
        db.session.flush()
        
        # [Rest of the donor creation code remains the same...]
        # Generate location coordinates
        lat = base_lat + random.uniform(-0.3, 0.3)
        lon = base_lon + random.uniform(-0.3, 0.3)
        
        # Determine eligibility
        if eligible_count < eligible_target:
            make_eligible = True
        else:
            make_eligible = random.random() < 0.3
        
        # Generate donation history
        total_donations = 0
        last_donation_date = None
        
        if make_eligible:
            total_donations = random.randint(1, 15)
            if total_donations > 0 and random.random() < 0.8:
                days_ago = random.randint(100, 365)
                last_donation_date = datetime.now() - timedelta(days=days_ago)
                eligible_count += 1
        else:
            total_donations = random.randint(0, 8)
            if total_donations > 0 and random.random() < 0.7:
                days_ago = random.randint(1, 89)
                last_donation_date = datetime.now() - timedelta(days=days_ago)
        
        # Create donor profile
        donor = Donor(
            donor_unique_id=donor_unique_id,
            user_id=user.id,
            blood_type=random.choice(BLOOD_TYPES),
            date_of_birth=dob,
            gender=random.choice(GENDERS),
            weight=random.randint(45, 100),
            nationality=random.choice(['Indian', 'Indian', 'Indian', 'Other']),
            has_disability=random.choice([False, False, False, True]),
            disability=random.choice([None, None, None, 'Mobility impairment', 'Visual impairment', 'Hearing impairment']),
            address=random_address(),
            city=city,
            state=state,
            pincode=random_pincode(),
            latitude=lat,
            longitude=lon,
            location_updated_at=datetime.now() - timedelta(days=random.randint(0, 30)),
            medical_conditions=random.choice([None, None, 'Mild Asthma', 'Controlled BP', 'Diabetes Type 2']),
            medications=random.choice([None, None, 'Blood pressure medication', 'Insulin']),
            last_donation_date=last_donation_date,
            total_donations=total_donations,
            is_available=random.choice([True, False]),
            is_eligible=make_eligible,
            emergency_contact_name=f"{random.choice(INDIAN_FIRST_NAMES)} {random.choice(INDIAN_LAST_NAMES)}",
            emergency_contact_phone=random_phone(),
            emergency_contact_relation=random.choice(['Spouse', 'Parent', 'Sibling', 'Friend', 'Child']),
            created_at=user.created_at
        )
        db.session.add(donor)
        donors.append(donor)
        
        # Create donation records (limited to 5 for performance)
        if total_donations > 0:
            donation_count = min(total_donations, 5)
            donation_dates = []
            
            for d in range(donation_count):
                if d == 0 and last_donation_date:
                    donation_date = last_donation_date
                else:
                    days_offset = random.randint(200, 800)
                    donation_date = (last_donation_date or datetime.now()) - timedelta(days=days_offset)
                donation_dates.append(donation_date)
            
            donation_dates.sort()
            
            for donation_date in donation_dates:
                donation = Donation(
                    donor_id=user.id,
                    donor_name=user.name,
                    donor_blood_type=donor.blood_type,
                    donation_date=donation_date,
                    units_donated=random.randint(1, 2),
                    donation_center=random.choice(['Red Cross Camp', 'City Hospital', 'Blood Bank', 'Mobile Camp']),
                    is_verified=random.choice([True, True, False]),
                    certificate_generated=random.choice([True, True, False]),
                    blood_pressure=f"{random.randint(110, 130)}/{random.randint(70, 90)}",
                    hemoglobin_level=round(random.uniform(12.0, 16.0), 1)
                )
                # Generate unique donation ID
                donation.donation_id = f"DON{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:6].upper()}"
                db.session.add(donation)
        
        # Commit in batches
        if (i + 1) % batch_size == 0:
            db.session.flush()
        
        progress.update(i + 1)
    
    db.session.commit()
    print(f"\n✅ Created {len(donors)} donors")
    print(f"   Eligible donors: {eligible_count} (target: {eligible_target}+)")
    return donors

# def create_blood_requests(donors, hospitals, count=5000):
#     """Create blood requests"""
#     print(f"\n📋 Creating {count} blood requests...")
#     requests = []
#     progress = ProgressBar(count, prefix='Progress:', suffix='Complete', length=50)
    
#     for i in range(count):
#         donor = random.choice(donors)
#         hospital = random.choice(hospitals) if hospitals else None
#         urgency = random.choice(URGENCY_LEVELS)
        
#         # Determine status based on urgency and randomness
#         if urgency == 'emergency':
#             status_weights = [0.3, 0.5, 0.1, 0.1]  # More likely fulfilled for emergency
#         else:
#             status_weights = [0.4, 0.3, 0.2, 0.1]
        
#         status = random.choices(REQUEST_STATUS, weights=status_weights)[0]
        
#         # Calculate dates
#         created_at = random_date(2023, 2025)
#         if urgency == 'emergency':
#             expires_at = created_at + timedelta(hours=48)
#         else:
#             expires_at = created_at + timedelta(days=random.randint(3, 10))
        
#         fulfilled_at = None
#         if status == 'fulfilled':
#             fulfilled_at = created_at + timedelta(hours=random.randint(1, 48))
        
#         # Create request
#         blood_request = BloodRequest(
#             requester_id=donor.user_id,
#             requester_name=donor.user.name,
#             requester_phone=donor.user.phone,
#             requester_email=donor.user.email,
#             requester_type=random.choice(['patient', 'relative', 'hospital', 'self']),
#             patient_name=f"Patient {random.choice(INDIAN_FIRST_NAMES)} {random.choice(INDIAN_LAST_NAMES)}",
#             patient_age=random.randint(1, 85),
#             patient_gender=random.choice(GENDERS),
#             blood_type_needed=random.choice(BLOOD_TYPES),
#             units_needed=random.randint(1, 5),
#             hospital_name=hospital.name if hospital else None,
#             hospital_address=hospital.address if hospital else None,
#             hospital_latitude=hospital.latitude if hospital else donor.latitude,
#             hospital_longitude=hospital.longitude if hospital else donor.longitude,
#             urgency=urgency,
#             status=status,
#             reason=random.choice(['Accident', 'Surgery', 'Childbirth', 'Thalassemia', 'Cancer Treatment', 'Anemia', None]),
#             required_by_date=(created_at + timedelta(days=random.randint(1, 7))).date(),
#             requester_latitude=donor.latitude,
#             requester_longitude=donor.longitude,
#             search_radius=random.choice([5, 10, 20, 50, 100]),
#             notified_donors=random.randint(0, 30),
#             accepted_donors=random.randint(0, 5),
#             created_at=created_at,
#             expires_at=expires_at,
#             fulfilled_at=fulfilled_at
#         )
#         db.session.add(blood_request)
#         requests.append(blood_request)
        
#         if (i + 1) % 100 == 0:
#             db.session.flush()
        
#         progress.update(i + 1)
    
#     db.session.commit()
#     print(f"✅ Created {len(requests)} blood requests")
#     return requests

def create_blood_requests(donors, hospitals, count=5000):
    """Create blood requests with guaranteed unique request IDs"""
    print(f"\n📋 Creating {count} blood requests...")
    requests = []
    progress = ProgressBar(count, prefix='Progress:', suffix='Complete', length=50)
    
    # Track used request IDs to avoid duplicates
    used_request_ids = set()
    
    for i in range(count):
        donor = random.choice(donors)
        hospital = random.choice(hospitals) if hospitals else None
        urgency = random.choice(URGENCY_LEVELS)
        
        # Determine status based on urgency and randomness
        if urgency == 'emergency':
            status_weights = [0.3, 0.5, 0.1, 0.1]  # More likely fulfilled for emergency
        else:
            status_weights = [0.4, 0.3, 0.2, 0.1]
        
        status = random.choices(REQUEST_STATUS, weights=status_weights)[0]
        
        # Calculate dates
        created_at = random_date(2023, 2025)
        if urgency == 'emergency':
            expires_at = created_at + timedelta(hours=48)
        else:
            expires_at = created_at + timedelta(days=random.randint(3, 10))
        
        fulfilled_at = None
        if status == 'fulfilled':
            fulfilled_at = created_at + timedelta(hours=random.randint(1, 48))
        
        # Generate unique request ID
        while True:
            # Use timestamp + random chars + counter to ensure uniqueness
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')[-8:]
            random_chars = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=6))
            request_id = f"REQ{timestamp}{random_chars}"
            
            if request_id not in used_request_ids:
                used_request_ids.add(request_id)
                break
        
        # Create request
        blood_request = BloodRequest(
            request_id=request_id,
            requester_id=donor.user_id,
            requester_name=donor.user.name,
            requester_phone=donor.user.phone,
            requester_email=donor.user.email,
            requester_type=random.choice(['patient', 'relative', 'hospital', 'self']),
            patient_name=f"Patient {random.choice(INDIAN_FIRST_NAMES)} {random.choice(INDIAN_LAST_NAMES)}",
            patient_age=random.randint(1, 85),
            patient_gender=random.choice(GENDERS),
            blood_type_needed=random.choice(BLOOD_TYPES),
            units_needed=random.randint(1, 5),
            hospital_name=hospital.name if hospital else None,
            hospital_address=hospital.address if hospital else None,
            hospital_latitude=hospital.latitude if hospital else donor.latitude,
            hospital_longitude=hospital.longitude if hospital else donor.longitude,
            urgency=urgency,
            status=status,
            reason=random.choice(['Accident', 'Surgery', 'Childbirth', 'Thalassemia', 'Cancer Treatment', 'Anemia', None]),
            required_by_date=(created_at + timedelta(days=random.randint(1, 7))).date(),
            requester_latitude=donor.latitude,
            requester_longitude=donor.longitude,
            search_radius=random.choice([5, 10, 20, 50, 100]),
            notified_donors=random.randint(0, 30),
            accepted_donors=random.randint(0, 5),
            created_at=created_at,
            expires_at=expires_at,
            fulfilled_at=fulfilled_at
        )
        db.session.add(blood_request)
        requests.append(blood_request)
        
        if (i + 1) % 100 == 0:
            db.session.flush()
        
        progress.update(i + 1)
    
    db.session.commit()
    print(f"✅ Created {len(requests)} blood requests")
    return requests

def print_statistics():
    """Print comprehensive database statistics"""
    print("\n" + "="*70)
    print("📊 DATABASE STATISTICS")
    print("="*70)
    
    # Basic counts
    print(f"\n📈 Basic Counts:")
    print(f"   👥 Users: {User.query.count():,}")
    print(f"   🩸 Donors: {Donor.query.count():,}")
    print(f"   🏥 Hospitals: {Hospital.query.count():,}")
    print(f"   📋 Blood Requests: {BloodRequest.query.count():,}")
    print(f"   🎁 Donations: {Donation.query.count():,}")
    print(f"   📝 Admin Logs: {AdminLog.query.count():,}")
    
    # Admin stats
    admins = User.query.filter_by(role='admin').count()
    print(f"\n👑 Admin Users: {admins}")
    
    # Donor eligibility
    eligible = Donor.query.filter_by(is_eligible=True).count()
    not_eligible = Donor.query.filter_by(is_eligible=False).count()
    print(f"\n✅ Eligible Donors: {eligible:,} ({(eligible/(eligible+not_eligible)*100):.1f}%)")
    print(f"❌ Not Eligible: {not_eligible:,}")
    
    # Blood type distribution
    print(f"\n🩸 Blood Type Distribution:")
    for bt in BLOOD_TYPES:
        count = Donor.query.filter_by(blood_type=bt).count()
        percentage = (count / Donor.query.count() * 100) if Donor.query.count() > 0 else 0
        print(f"   {bt}: {count:,} ({percentage:.1f}%)")
    
    # Gender distribution
    print(f"\n👤 Gender Distribution:")
    for gender in GENDERS:
        count = Donor.query.filter_by(gender=gender).count()
        if count > 0:
            percentage = (count / Donor.query.count() * 100) if Donor.query.count() > 0 else 0
            print(f"   {gender.title()}: {count:,} ({percentage:.1f}%)")
    
    # Hospital stats
    verified_hospitals = Hospital.query.filter_by(is_verified=True).count()
    blood_bank_hospitals = Hospital.query.filter_by(has_blood_bank=True).count()
    print(f"\n🏥 Hospital Statistics:")
    print(f"   Verified Hospitals: {verified_hospitals:,} ({(verified_hospitals/Hospital.query.count()*100):.1f}%)")
    print(f"   With Blood Bank: {blood_bank_hospitals:,}")
    
    # Request stats
    pending = BloodRequest.query.filter_by(status='pending').count()
    fulfilled = BloodRequest.query.filter_by(status='fulfilled').count()
    emergency = BloodRequest.query.filter_by(urgency='emergency', status='pending').count()
    print(f"\n📋 Request Status:")
    print(f"   Pending: {pending:,}")
    print(f"   Fulfilled: {fulfilled:,}")
    print(f"   Emergency (pending): {emergency:,}")
    
    # Geographic distribution
    print(f"\n🌍 Geographic Distribution (Top 10 Cities):")
    from sqlalchemy import func
    city_stats = db.session.query(Donor.city, func.count(Donor.id)).group_by(Donor.city).order_by(func.count(Donor.id).desc()).limit(10).all()
    for city, count in city_stats:
        print(f"   {city}: {count:,}")
    
    # Age distribution
    print(f"\n📊 Age Distribution:")
    donors = Donor.query.all()
    age_groups = {'18-25': 0, '26-35': 0, '36-45': 0, '46-55': 0, '56-65': 0}
    for donor in donors:
        age = donor.calculate_age()
        if 18 <= age <= 25:
            age_groups['18-25'] += 1
        elif 26 <= age <= 35:
            age_groups['26-35'] += 1
        elif 36 <= age <= 45:
            age_groups['36-45'] += 1
        elif 46 <= age <= 55:
            age_groups['46-55'] += 1
        elif 56 <= age <= 65:
            age_groups['56-65'] += 1
    
    for group, count in age_groups.items():
        print(f"   {group}: {count:,}")

def verify_eligible_donors(target=2000):
    """Verify that we have at least target eligible donors"""
    eligible = Donor.query.filter_by(is_eligible=True).count()
    if eligible >= target:
        print(f"\n✅ SUCCESS: {eligible} eligible donors (target: {target}+)")
        return True
    else:
        print(f"\n⚠️ WARNING: Only {eligible} eligible donors (target: {target}+)")
        return False

# ==================== MAIN FUNCTION ====================

def main():
    """Main function to populate database"""
    print("="*80)
    print("🚀 COMPLETE DATABASE POPULATION SCRIPT")
    print("="*80)
    print("\nThis script will create:")
    print("  • 5,000+ blood donors (with 2,000+ eligible)")
    print("  • 5,000+ hospitals")
    print("  • 5 admin users")
    print("  • 5,000+ blood requests")
    print("  • Donation records")
    print("\n⚠️  This will CLEAR ALL EXISTING DATA!")
    
    # Confirm
    response = input("\nDo you want to continue? (yes/no): ").strip().lower()
    if response != 'yes':
        print("❌ Operation cancelled")
        return
    
    app = create_app()
    start_time = time.time()
    
    with app.app_context():
        # Clear existing data
        print("\n🗑️  Clearing existing data...")
        db.session.query(Donation).delete()
        db.session.query(BloodRequest).delete()
        db.session.query(Donor).delete()
        db.session.query(Hospital).delete()
        db.session.query(AdminLog).delete()
        db.session.query(User).filter(User.role != 'admin').delete()  # Keep existing admins? No, clear all
        db.session.query(User).delete()
        db.session.commit()
        print("✅ Database cleared")
        
        # Create data in sequence
        admins = create_admins(5)
        hospitals = create_hospitals(5000)
        donors = create_donors(5000, 2000)
        requests = create_blood_requests(donors, hospitals, 5000)
        
        # Final commit
        db.session.commit()
        
        # Print statistics
        print_statistics()
        verify_eligible_donors(2000)
        
        # Calculate time
        elapsed = time.time() - start_time
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        
        print("\n" + "="*80)
        print(f"✅ DATABASE POPULATION COMPLETE!")
        print(f"⏱️  Time taken: {minutes}m {seconds}s")
        print("="*80)
        print("\n📝 Login Credentials:")
        print("   • Admin users: [any admin email] / Admin@123")
        print("   • Donors: [any donor email] / Donor@123")
        print("\n🔗 Test these URLs:")
        print("   • Admin Dashboard: http://127.0.0.1:5000/admin/dashboard")
        print("   • Donor Dashboard: http://127.0.0.1:5000/donor/dashboard")
        print("   • Nearby Donors: http://127.0.0.1:5000/donor/nearby-donors")
        print("   • Nearby Hospitals: http://127.0.0.1:5000/donor/nearby-hospitals")

if __name__ == "__main__":
    main()