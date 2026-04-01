"""
Donor Tests - Test donor functionality
"""

import unittest
import sys
import os
from datetime import date, datetime, timedelta
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.user import User
from app.models.donor import Donor
from app.models.donation import Donation
from app.services.eligibility_service import EligibilityService

class DonorTestCase(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['WTF_CSRF_ENABLED'] = False
        
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        
        db.create_all()
        
        # Create test donor
        self.create_test_donor()
    
    def tearDown(self):
        """Clean up after tests"""
        db.session.remove()
        db.drop_all()
        self.ctx.pop()
    
    def create_test_donor(self):
        """Create test donor"""
        # Create user
        user = User(
            email='donor@test.com',
            name='Test Donor',
            phone='1234567890',
            role='donor'
        )
        user.set_password('password')
        db.session.add(user)
        db.session.flush()
        
        # Create donor
        donor = Donor(
            user_id=user.id,
            blood_type='O+',
            date_of_birth=date(1990, 1, 1),
            gender='male',
            weight=70,
            address='Test Address',
            city='Test City',
            state='Test State',
            pincode='123456',
            emergency_contact_name='Emergency Contact',
            emergency_contact_phone='0987654321',
            emergency_contact_relation='Friend',
            latitude=28.6139,
            longitude=77.2090,
            is_available=True
        )
        db.session.add(donor)
        db.session.commit()
        
        self.user = user
        self.donor = donor
    
    def test_donor_creation(self):
        """Test donor creation"""
        self.assertIsNotNone(self.donor.id)
        self.assertEqual(self.donor.blood_type, 'O+')
        self.assertEqual(self.donor.user.name, 'Test Donor')
    
    def test_donor_age_calculation(self):
        """Test age calculation"""
        age = self.donor.calculate_age()
        expected_age = date.today().year - 1990
        self.assertEqual(age, expected_age)
    
    def test_donor_eligibility_new(self):
        """Test eligibility for new donor"""
        is_eligible, message, next_date = self.donor.check_eligibility()
        self.assertTrue(is_eligible)
        self.assertIsNone(next_date)
    
    def test_donor_eligibility_recent_donation(self):
        """Test eligibility with recent donation"""
        # Add recent donation
        donation = Donation(
            donor_id=self.user.id,
            donor_name=self.user.name,
            donor_blood_type=self.donor.blood_type,
            donation_date=datetime.now() - timedelta(days=30)
        )
        db.session.add(donation)
        
        self.donor.last_donation_date = donation.donation_date
        db.session.commit()
        
        is_eligible, message, next_date = self.donor.check_eligibility()
        self.assertFalse(is_eligible)
        self.assertIsNotNone(next_date)
    
    def test_donor_eligibility_weight(self):
        """Test eligibility with low weight"""
        self.donor.weight = 40
        is_eligible, message, next_date = self.donor.check_eligibility()
        self.assertFalse(is_eligible)
        self.assertIn('weight', message.lower())
    
    def test_donor_eligibility_age_too_young(self):
        """Test eligibility with underage donor"""
        self.donor.date_of_birth = date.today() - timedelta(days=365*10)
        is_eligible, message, next_date = self.donor.check_eligibility()
        self.assertFalse(is_eligible)
        self.assertIn('age', message.lower())
    
    def test_donor_update_location(self):
        """Test location update"""
        new_lat = 19.0760
        new_lon = 72.8777
        
        self.donor.latitude = new_lat
        self.donor.longitude = new_lon
        self.donor.location_updated_at = datetime.utcnow()
        db.session.commit()
        
        self.assertEqual(self.donor.latitude, new_lat)
        self.assertEqual(self.donor.longitude, new_lon)
    
    def test_donor_availability_toggle(self):
        """Test availability toggle"""
        self.assertTrue(self.donor.is_available)
        
        self.donor.is_available = False
        db.session.commit()
        
        self.assertFalse(self.donor.is_available)
    
    def test_donor_donation_record(self):
        """Test donation recording"""
        initial_count = self.donor.total_donations
        
        self.donor.total_donations += 1
        self.donor.last_donation_date = datetime.utcnow()
        db.session.commit()
        
        self.assertEqual(self.donor.total_donations, initial_count + 1)
        self.assertIsNotNone(self.donor.last_donation_date)
    
    def test_donor_medical_conditions(self):
        """Test medical conditions"""
        self.donor.medical_conditions = 'diabetes'
        is_eligible, message, next_date = self.donor.check_eligibility()
        self.assertFalse(is_eligible)
        self.assertIn('medical condition', message.lower())
    
    def test_donor_to_dict(self):
        """Test donor serialization"""
        donor_dict = self.donor.to_dict()
        
        self.assertEqual(donor_dict['name'], self.user.name)
        self.assertEqual(donor_dict['blood_type'], self.donor.blood_type)
        self.assertEqual(donor_dict['city'], self.donor.city)
        self.assertEqual(donor_dict['latitude'], self.donor.latitude)
        self.assertEqual(donor_dict['longitude'], self.donor.longitude)
    
    def test_donor_next_eligible_date(self):
        """Test next eligible date calculation"""
        # No previous donation
        next_date = self.donor.get_next_eligible_date()
        self.assertEqual(next_date, datetime.now().date())
        
        # With previous donation
        self.donor.last_donation_date = datetime.now() - timedelta(days=30)
        next_date = self.donor.get_next_eligible_date()
        expected_date = self.donor.last_donation_date.date() + timedelta(days=90)
        self.assertEqual(next_date, expected_date)

if __name__ == '__main__':
    unittest.main()