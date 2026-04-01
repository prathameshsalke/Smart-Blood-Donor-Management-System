"""
API Tests - Test API endpoints
"""

import unittest
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.user import User
from app.models.donor import Donor
from app.models.hospital import Hospital
from app.models.blood_request import BloodRequest

class APITestCase(unittest.TestCase):
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
        
        # Create test data
        self.create_test_data()
    
    def tearDown(self):
        """Clean up after tests"""
        db.session.remove()
        db.drop_all()
        self.ctx.pop()
    
    def create_test_data(self):
        """Create test data"""
        # Create test user
        user = User(
            email='test@example.com',
            name='Test User',
            phone='1234567890',
            role='donor'
        )
        user.set_password('password')
        db.session.add(user)
        
        # Create test donor
        donor = Donor(
            user_id=user.id,
            blood_type='O+',
            date_of_birth='1990-01-01',
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
        
        # Create test hospital
        hospital = Hospital(
            name='Test Hospital',
            phone='1234567890',
            address='Hospital Address',
            city='Test City',
            state='Test State',
            pincode='123456',
            latitude=28.6145,
            longitude=77.2095,
            is_verified=True
        )
        db.session.add(hospital)
        
        db.session.commit()
        
        self.test_user = user
        self.test_donor = donor
        self.test_hospital = hospital
    
    def test_nearby_donors_api(self):
        """Test nearby donors API"""
        response = self.client.get(
            '/api/donors/nearby?lat=28.6139&lon=77.2090&radius=10'
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('donors', data)
    
    def test_nearby_hospitals_api(self):
        """Test nearby hospitals API"""
        response = self.client.get(
            '/api/hospitals/nearby?lat=28.6139&lon=77.2090&radius=10'
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('hospitals', data)
    
    def test_emergency_request_api(self):
        """Test emergency request API"""
        # Login first
        self.client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'password'
        })
        
        response = self.client.post('/api/requests/emergency',
            json={
                'patient_name': 'Emergency Patient',
                'blood_type': 'O+',
                'requester_name': 'Requester',
                'requester_phone': '1234567890',
                'requester_latitude': 28.6139,
                'requester_longitude': 77.2090
            }
        )
        
        self.assertEqual(response.status_code, 201)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('request_id', data)
    
    def test_donor_availability_api(self):
        """Test donor availability API"""
        response = self.client.get(f'/api/donors/{self.test_donor.id}/availability')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('is_available', data)
    
    def test_donor_donations_api(self):
        """Test donor donations API"""
        response = self.client.get(f'/api/donors/{self.test_donor.id}/donations')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('donations', data)
    
    def test_hospital_details_api(self):
        """Test hospital details API"""
        response = self.client.get(f'/api/hospitals/{self.test_hospital.id}')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['hospital']['name'], 'Test Hospital')
    
    def test_stats_api(self):
        """Test stats API"""
        response = self.client.get('/api/stats')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('stats', data)
    
    def test_health_api(self):
        """Test health check API"""
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')

if __name__ == '__main__':
    unittest.main()