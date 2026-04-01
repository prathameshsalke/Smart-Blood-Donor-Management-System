"""
Services Tests - Test service layer functionality
"""

import unittest
import sys
import os
from datetime import date, datetime, timedelta
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.user import User
from app.models.donor import Donor
from app.models.blood_request import BloodRequest
from app.models.hospital import Hospital
from app.services.geo_service import GeoService
from app.services.eligibility_service import EligibilityService
from app.services.matching_service import MatchingService

class ServicesTestCase(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        
        db.create_all()
        
        # Create test data
        self.create_test_data()
    
    def tearDown(self):
        """Clean up after tests"""
        db.session.remove()
        db.drop_all()
        self.ctx.pop()
    
    def create_test_data(self):
        """Create test data"""
        # Create donors at different locations
        locations = [
            (28.6139, 77.2090, 'Delhi'),  # Delhi
            (19.0760, 72.8777, 'Mumbai'), # Mumbai
            (12.9716, 77.5946, 'Bangalore'), # Bangalore
            (13.0827, 80.2707, 'Chennai'), # Chennai
            (22.5726, 88.3639, 'Kolkata') # Kolkata
        ]
        
        blood_types = ['O+', 'A+', 'B+', 'AB+', 'O-']
        
        for i, (lat, lon, city) in enumerate(locations):
            user = User(
                email=f'donor{i}@test.com',
                name=f'Donor {i}',
                phone=f'1234567{i:03d}',
                role='donor'
            )
            user.set_password('password')
            db.session.add(user)
            db.session.flush()
            
            donor = Donor(
                user_id=user.id,
                blood_type=blood_types[i % len(blood_types)],
                date_of_birth=date(1990, 1, 1),
                gender='male',
                weight=70,
                address=f'Address {city}',
                city=city,
                state='Test State',
                pincode='123456',
                emergency_contact_name='Emergency Contact',
                emergency_contact_phone=f'9987654{i:03d}',
                emergency_contact_relation='Friend',
                latitude=lat,
                longitude=lon,
                is_available=True
            )
            db.session.add(donor)
        
        # Create test hospital
        hospital = Hospital(
            name='Central Hospital',
            phone='1122334455',
            address='Hospital Road',
            city='Delhi',
            state='Delhi',
            pincode='110001',
            latitude=28.6145,
            longitude=77.2095,
            is_verified=True,
            has_blood_bank=True
        )
        db.session.add(hospital)
        
        db.session.commit()
        
        self.donors = Donor.query.all()
        self.hospital = hospital
    
    def test_geo_service_haversine(self):
        """Test Haversine distance calculation"""
        # Delhi to Mumbai distance (approx 1150 km)
        distance = GeoService.haversine_distance(28.6139, 77.2090, 19.0760, 72.8777)
        self.assertAlmostEqual(distance, 1150, delta=50)
    
    def test_geo_service_geodesic(self):
        """Test geodesic distance calculation"""
        distance = GeoService.geodesic_distance(28.6139, 77.2090, 28.6145, 77.2095)
        self.assertAlmostEqual(distance, 0.07, delta=0.02)
    
    def test_geo_service_find_nearby_donors(self):
        """Test finding nearby donors"""
        donors = GeoService.find_nearby_donors(28.6139, 77.2090, radius_km=50)
        self.assertGreaterEqual(len(donors), 1)  # At least Delhi donor
    
    def test_geo_service_find_nearby_hospitals(self):
        """Test finding nearby hospitals"""
        hospitals = GeoService.find_nearby_hospitals(28.6139, 77.2090, radius_km=10)
        self.assertEqual(len(hospitals), 1)
        self.assertEqual(hospitals[0]['name'], 'Central Hospital')
    
    def test_geo_service_bounding_box(self):
        """Test bounding box calculation"""
        min_lat, max_lat, min_lon, max_lon = GeoService.get_bounding_box(
            28.6139, 77.2090, 10
        )
        self.assertLess(min_lat, 28.6139)
        self.assertGreater(max_lat, 28.6139)
        self.assertLess(min_lon, 77.2090)
        self.assertGreater(max_lon, 77.2090)
    
    def test_eligibility_service_check(self):
        """Test eligibility check"""
        donor = self.donors[0]
        is_eligible, message, next_date = EligibilityService.check_eligibility(donor)
        self.assertTrue(is_eligible)
    
    def test_eligibility_service_summary(self):
        """Test eligibility summary"""
        donor = self.donors[0]
        summary = EligibilityService.get_eligibility_summary(donor)
        self.assertIn('is_eligible', summary)
        self.assertIn('age', summary)
        self.assertIn('weight', summary)
    
    def test_matching_service_find_matches(self):
        """Test finding matching donors"""
        # Create blood request
        request = BloodRequest(
            patient_name='Test Patient',
            blood_type_needed='O+',
            units_needed=1,
            requester_name='Requester',
            requester_phone='1234567890',
            requester_latitude=28.6139,
            requester_longitude=77.2090,
            search_radius=100
        )
        
        matches = MatchingService.find_matching_donors(request)
        self.assertGreater(len(matches), 0)
    
    def test_matching_service_match_score(self):
        """Test match score calculation"""
        donor = self.donors[0]
        request = BloodRequest(
            patient_name='Test Patient',
            blood_type_needed='O+',
            units_needed=1,
            requester_name='Requester',
            requester_phone='1234567890',
            requester_latitude=28.6139,
            requester_longitude=77.2090
        )
        
        score = MatchingService._calculate_match_score(donor, request, 5.0)
        self.assertGreater(score, 0)
        self.assertLess(score, 200)

if __name__ == '__main__':
    unittest.main()