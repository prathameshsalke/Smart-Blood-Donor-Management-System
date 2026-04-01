"""
Donor Validator - Validate donor profile inputs
"""

import re
from datetime import datetime, date
from marshmallow import Schema, fields, validate, ValidationError, validates_schema

class DonorValidator:
    """Donor profile input validator"""
    
    @staticmethod
    def validate_blood_type(blood_type):
        """Validate blood type"""
        valid_types = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        if blood_type not in valid_types:
            raise ValidationError(f'Blood type must be one of: {", ".join(valid_types)}')
        return True
    
    @staticmethod
    def validate_date_of_birth(dob):
        """Validate date of birth"""
        if not isinstance(dob, (date, datetime)):
            raise ValidationError('Invalid date format')
        
        today = date.today()
        age = today.year - dob.year
        
        if today.month < dob.month or (today.month == dob.month and today.day < dob.day):
            age -= 1
        
        if age < 18:
            raise ValidationError('Donor must be at least 18 years old')
        
        if age > 65:
            raise ValidationError('Donor must be under 65 years old')
        
        return True
    
    @staticmethod
    def validate_weight(weight):
        """Validate weight"""
        if weight < 45:
            raise ValidationError('Weight must be at least 45 kg')
        
        if weight > 200:
            raise ValidationError('Weight must be less than 200 kg')
        
        return True
    
    @staticmethod
    def validate_gender(gender):
        """Validate gender"""
        valid_genders = ['male', 'female', 'other']
        if gender not in valid_genders:
            raise ValidationError(f'Gender must be one of: {", ".join(valid_genders)}')
        return True
    
    @staticmethod
    def validate_pincode(pincode):
        """Validate pincode"""
        # Remove any spaces
        pincode = str(pincode).strip()
        
        if not pincode.isdigit():
            raise ValidationError('Pincode must contain only digits')
        
        if len(pincode) != 6:
            raise ValidationError('Pincode must be 6 digits')
        
        return True
    
    @staticmethod
    def validate_emergency_contact(contact):
        """Validate emergency contact"""
        if not contact:
            raise ValidationError('Emergency contact is required')
        
        # Check if it's a name or phone
        if contact.isdigit():
            # It's a phone number
            if len(contact) != 10:
                raise ValidationError('Emergency contact phone must be 10 digits')
        else:
            # It's a name
            if len(contact) < 2:
                raise ValidationError('Emergency contact name must be at least 2 characters')
        
        return True
    
    @staticmethod
    def validate_medical_conditions(conditions):
        """Validate medical conditions (optional)"""
        if conditions and len(conditions) > 1000:
            raise ValidationError('Medical conditions description too long (max 1000 characters)')
        return True
    
    @staticmethod
    def validate_location(lat, lon):
        """Validate location coordinates"""
        if lat is not None:
            if not -90 <= lat <= 90:
                raise ValidationError('Latitude must be between -90 and 90')
        
        if lon is not None:
            if not -180 <= lon <= 180:
                raise ValidationError('Longitude must be between -180 and 180')
        
        return True
    
    @staticmethod
    def validate_donor_profile_data(data):
        """Validate complete donor profile data"""
        required_fields = [
            'blood_type', 'date_of_birth', 'gender', 'weight',
            'address', 'city', 'state', 'pincode',
            'emergency_contact_name', 'emergency_contact_phone'
        ]
        
        for field in required_fields:
            if field not in data:
                raise ValidationError(f'{field} is required')
            
            if not data[field]:
                raise ValidationError(f'{field} cannot be empty')
        
        # Validate each field
        DonorValidator.validate_blood_type(data['blood_type'])
        DonorValidator.validate_date_of_birth(data['date_of_birth'])
        DonorValidator.validate_gender(data['gender'])
        DonorValidator.validate_weight(data['weight'])
        DonorValidator.validate_pincode(data['pincode'])
        
        # Validate emergency contact
        DonorValidator.validate_emergency_contact(data['emergency_contact_name'])
        DonorValidator.validate_emergency_contact(data['emergency_contact_phone'])
        
        # Validate location if provided
        if 'latitude' in data and 'longitude' in data:
            if data['latitude'] and data['longitude']:
                DonorValidator.validate_location(data['latitude'], data['longitude'])
        
        return True

class DonorProfileSchema(Schema):
    """Donor profile data schema"""
    blood_type = fields.Str(required=True)
    date_of_birth = fields.Date(required=True)
    gender = fields.Str(required=True)
    weight = fields.Float(required=True, validate=validate.Range(min=45, max=200))
    address = fields.Str(required=True)
    city = fields.Str(required=True)
    state = fields.Str(required=True)
    pincode = fields.Str(required=True, validate=validate.Length(6, 6))
    medical_conditions = fields.Str(allow_none=True)
    medications = fields.Str(allow_none=True)
    emergency_contact_name = fields.Str(required=True)
    emergency_contact_phone = fields.Str(required=True, validate=validate.Length(10, 10))
    emergency_contact_relation = fields.Str(required=True)
    latitude = fields.Float(allow_none=True)
    longitude = fields.Float(allow_none=True)
    
    @validates_schema
    def validate_all(self, data, **kwargs):
        DonorValidator.validate_donor_profile_data(data)

class DonorUpdateSchema(Schema):
    """Donor update data schema"""
    address = fields.Str()
    city = fields.Str()
    state = fields.Str()
    pincode = fields.Str(validate=validate.Length(6, 6))
    medical_conditions = fields.Str(allow_none=True)
    medications = fields.Str(allow_none=True)
    is_available = fields.Bool()
    emergency_contact_name = fields.Str()
    emergency_contact_phone = fields.Str(validate=validate.Length(10, 10))
    emergency_contact_relation = fields.Str()
    latitude = fields.Float()
    longitude = fields.Float()