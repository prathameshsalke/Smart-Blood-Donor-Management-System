"""
Auth Validator - Validate authentication inputs
"""

import re
from marshmallow import Schema, fields, validate, ValidationError, validates_schema
from datetime import datetime

class AuthValidator:
    """Authentication input validator"""
    
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise ValidationError('Invalid email format')
        return True
    
    @staticmethod
    def validate_phone(phone):
        """Validate phone number"""
        # Remove any non-digit characters
        phone = re.sub(r'\D', '', phone)
        
        if len(phone) != 10:
            raise ValidationError('Phone number must be 10 digits')
        
        if not phone.isdigit():
            raise ValidationError('Phone number must contain only digits')
        
        return True
    
    @staticmethod
    def validate_password(password):
        """Validate password strength"""
        if len(password) < 8:
            raise ValidationError('Password must be at least 8 characters long')
        
        if not any(c.isupper() for c in password):
            raise ValidationError('Password must contain at least one uppercase letter')
        
        if not any(c.islower() for c in password):
            raise ValidationError('Password must contain at least one lowercase letter')
        
        if not any(c.isdigit() for c in password):
            raise ValidationError('Password must contain at least one number')
        
        if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
            raise ValidationError('Password must contain at least one special character')
        
        return True
    
    @staticmethod
    def validate_name(name):
        """Validate name"""
        if len(name) < 2:
            raise ValidationError('Name must be at least 2 characters long')
        
        if len(name) > 100:
            raise ValidationError('Name must be less than 100 characters')
        
        if not re.match(r'^[a-zA-Z\s\'-]+$', name):
            raise ValidationError('Name contains invalid characters')
        
        return True
    
    @staticmethod
    def validate_login_data(data):
        """Validate login data"""
        required_fields = ['email', 'password']
        
        for field in required_fields:
            if field not in data:
                raise ValidationError(f'{field} is required')
            
            if not data[field]:
                raise ValidationError(f'{field} cannot be empty')
        
        AuthValidator.validate_email(data['email'])
        
        return True
    
    @staticmethod
    def validate_registration_data(data):
        """Validate registration data"""
        required_fields = ['email', 'password', 'confirm_password', 'name', 'phone']
        
        for field in required_fields:
            if field not in data:
                raise ValidationError(f'{field} is required')
            
            if not data[field]:
                raise ValidationError(f'{field} cannot be empty')
        
        # Validate email
        AuthValidator.validate_email(data['email'])
        
        # Validate name
        AuthValidator.validate_name(data['name'])
        
        # Validate phone
        AuthValidator.validate_phone(data['phone'])
        
        # Validate password
        AuthValidator.validate_password(data['password'])
        
        # Check password confirmation
        if data['password'] != data['confirm_password']:
            raise ValidationError('Passwords do not match')
        
        return True
    
    @staticmethod
    def validate_password_reset(data):
        """Validate password reset data"""
        if 'token' not in data:
            raise ValidationError('Token is required')
        
        if 'new_password' not in data:
            raise ValidationError('New password is required')
        
        if 'confirm_password' not in data:
            raise ValidationError('Please confirm your password')
        
        AuthValidator.validate_password(data['new_password'])
        
        if data['new_password'] != data['confirm_password']:
            raise ValidationError('Passwords do not match')
        
        return True

class RegistrationSchema(Schema):
    """Registration data schema"""
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=8))
    confirm_password = fields.Str(required=True)
    name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    phone = fields.Str(required=True, validate=validate.Length(min=10, max=10))
    
    @validates_schema
    def validate_passwords(self, data, **kwargs):
        if data['password'] != data['confirm_password']:
            raise ValidationError('Passwords do not match')

class LoginSchema(Schema):
    """Login data schema"""
    email = fields.Email(required=True)
    password = fields.Str(required=True)
    remember = fields.Bool(load_default=False, dump_default=False)