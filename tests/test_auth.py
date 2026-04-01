"""
Unit tests for authentication module
"""

import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.user import User
from app.models.donor import Donor
from flask import url_for
from datetime import date

class AuthTestCase(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['WTF_CSRF_ENABLED'] = False
        
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
    
    def tearDown(self):
        """Clean up after tests"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_register_page(self):
        """Test registration page loads"""
        response = self.client.get('/auth/register')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Register', response.data)
    
    def test_login_page(self):
        """Test login page loads"""
        response = self.client.get('/auth/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)
    
    def test_user_registration(self):
        """Test user registration"""
        response = self.client.post('/auth/register', data={
            'name': 'Test User',
            'email': 'test@example.com',
            'phone': '1234567890',
            'password': 'password123',
            'confirm_password': 'password123',
            'blood_type': 'O+',
            'date_of_birth': '1990-01-01',
            'gender': 'male',
            'weight': 70,
            'address': 'Test Address',
            'city': 'Test City',
            'state': 'Test State',
            'pincode': '123456',
            'emergency_contact_name': 'Emergency Contact',
            'emergency_contact_phone': '0987654321',
            'emergency_contact_relation': 'Friend'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Registration successful', response.data)
        
        # Check if user was created
        with self.app.app_context():
            user = User.query.filter_by(email='test@example.com').first()
            self.assertIsNotNone(user)
            self.assertEqual(user.name, 'Test User')
            
            donor = Donor.query.filter_by(user_id=user.id).first()
            self.assertIsNotNone(donor)
            self.assertEqual(donor.blood_type, 'O+')
    
    def test_duplicate_registration(self):
        """Test registration with existing email"""
        # Create first user
        with self.app.app_context():
            user = User(
                email='test@example.com',
                name='Test User',
                phone='1234567890'
            )
            user.set_password('password')
            db.session.add(user)
            db.session.commit()
        
        # Try to register with same email
        response = self.client.post('/auth/register', data={
            'name': 'Another User',
            'email': 'test@example.com',
            'phone': '0987654321',
            'password': 'password123',
            'confirm_password': 'password123',
            'blood_type': 'A+',
            'date_of_birth': '1990-01-01',
            'gender': 'female',
            'weight': 60,
            'address': 'Test Address',
            'city': 'Test City',
            'state': 'Test State',
            'pincode': '123456',
            'emergency_contact_name': 'Emergency Contact',
            'emergency_contact_phone': '0987654321',
            'emergency_contact_relation': 'Friend'
        }, follow_redirects=True)
        
        self.assertIn(b'Email already registered', response.data)
    
    def test_user_login(self):
        """Test user login"""
        # Create user
        with self.app.app_context():
            user = User(
                email='test@example.com',
                name='Test User',
                phone='1234567890'
            )
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
        
        # Test login
        response = self.client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome back', response.data)
    
    def test_invalid_login(self):
        """Test login with invalid credentials"""
        response = self.client.post('/auth/login', data={
            'email': 'wrong@example.com',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        
        self.assertIn(b'Invalid email or password', response.data)
    
    def test_logout(self):
        """Test user logout"""
        # Login first
        with self.app.app_context():
            user = User(
                email='test@example.com',
                name='Test User',
                phone='1234567890'
            )
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
        
        self.client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        })
        
        # Test logout
        response = self.client.get('/auth/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'logged out', response.data)

if __name__ == '__main__':
    unittest.main()