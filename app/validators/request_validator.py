"""
Request Validator - Validate blood request inputs
"""

from datetime import datetime, date
from marshmallow import Schema, fields, validate, ValidationError, validates_schema

class RequestValidator:
    """Blood request input validator"""
    
    @staticmethod
    def validate_blood_type(blood_type):
        """Validate blood type"""
        valid_types = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        if blood_type not in valid_types:
            raise ValidationError(f'Blood type must be one of: {", ".join(valid_types)}')
        return True
    
    @staticmethod
    def validate_urgency(urgency):
        """Validate urgency level"""
        valid_levels = ['low', 'medium', 'high', 'emergency']
        if urgency not in valid_levels:
            raise ValidationError(f'Urgency must be one of: {", ".join(valid_levels)}')
        return True
    
    @staticmethod
    def validate_units(units):
        """Validate units needed"""
        if not isinstance(units, int):
            raise ValidationError('Units must be an integer')
        
        if units < 1:
            raise ValidationError('Units needed must be at least 1')
        
        if units > 10:
            raise ValidationError('Units needed cannot exceed 10')
        
        return True
    
    @staticmethod
    def validate_phone(phone):
        """Validate phone number"""
        # Remove any non-digit characters
        phone = re.sub(r'\D', '', str(phone))
        
        if len(phone) != 10:
            raise ValidationError('Phone number must be 10 digits')
        
        return True
    
    @staticmethod
    def validate_patient_age(age):
        """Validate patient age"""
        if age is not None:
            if not isinstance(age, int):
                raise ValidationError('Age must be an integer')
            
            if age < 0:
                raise ValidationError('Age cannot be negative')
            
            if age > 120:
                raise ValidationError('Please verify age (max 120)')
        
        return True
    
    @staticmethod
    def validate_required_by_date(required_date):
        """Validate required by date"""
        if required_date:
            if required_date < date.today():
                raise ValidationError('Required by date cannot be in the past')
        
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
    def validate_search_radius(radius):
        """Validate search radius"""
        if not isinstance(radius, (int, float)):
            raise ValidationError('Radius must be a number')
        
        if radius < 1:
            raise ValidationError('Search radius must be at least 1 km')
        
        if radius > 100:
            raise ValidationError('Search radius cannot exceed 100 km')
        
        return True
    
    @staticmethod
    def validate_request_data(data):
        """Validate blood request data"""
        required_fields = [
            'patient_name', 'blood_type_needed', 'units_needed',
            'requester_name', 'requester_phone',
            'requester_latitude', 'requester_longitude'
        ]
        
        for field in required_fields:
            if field not in data:
                raise ValidationError(f'{field} is required')
            
            if not data[field]:
                raise ValidationError(f'{field} cannot be empty')
        
        # Validate fields
        RequestValidator.validate_blood_type(data['blood_type_needed'])
        RequestValidator.validate_units(data['units_needed'])
        RequestValidator.validate_phone(data['requester_phone'])
        RequestValidator.validate_location(
            data['requester_latitude'],
            data['requester_longitude']
        )
        
        # Validate optional fields
        if 'urgency' in data and data['urgency']:
            RequestValidator.validate_urgency(data['urgency'])
        
        if 'patient_age' in data and data['patient_age']:
            RequestValidator.validate_patient_age(data['patient_age'])
        
        if 'required_by_date' in data and data['required_by_date']:
            RequestValidator.validate_required_by_date(data['required_by_date'])
        
        if 'search_radius' in data and data['search_radius']:
            RequestValidator.validate_search_radius(data['search_radius'])
        
        return True
    
    @staticmethod
    def validate_emergency_request(data):
        """Validate emergency request (simplified)"""
        required_fields = [
            'patient_name', 'blood_type_needed',
            'requester_name', 'requester_phone',
            'requester_latitude', 'requester_longitude'
        ]
        
        for field in required_fields:
            if field not in data:
                raise ValidationError(f'{field} is required')
            
            if not data[field]:
                raise ValidationError(f'{field} cannot be empty')
        
        # Validate fields
        RequestValidator.validate_blood_type(data['blood_type_needed'])
        RequestValidator.validate_phone(data['requester_phone'])
        RequestValidator.validate_location(
            data['requester_latitude'],
            data['requester_longitude']
        )
        
        return True

class BloodRequestSchema(Schema):
    """Blood request data schema"""
    patient_name = fields.Str(required=True)
    patient_age = fields.Int(allow_none=True)
    patient_gender = fields.Str(allow_none=True)
    blood_type_needed = fields.Str(required=True)
    #units_needed = fields.Int(required=True, validate=validate.Range(min=1, max=10))
    units_needed = fields.Int(load_default=1, validate=validate.Range(min=1, max=10))
    
    requester_name = fields.Str(required=True)
    requester_phone = fields.Str(required=True)
    requester_email = fields.Email(allow_none=True)
    requester_type = fields.Str(allow_none=True)
    
    hospital_name = fields.Str(allow_none=True)
    hospital_address = fields.Str(allow_none=True)
    
    #urgency = fields.Str(load_default='medium', dump_default='medium')
    urgency = fields.Str(load_default='medium')
    reason = fields.Str(allow_none=True)
    required_by_date = fields.Date(allow_none=True)
    
    requester_latitude = fields.Float(required=True)
    requester_longitude = fields.Float(required=True)
    #search_radius = fields.Int(load_default=10, dump_default=10)
    #search_radius = fields.Int(load_default=10)
    search_radius = fields.Int(load_default=10)
    
    @validates_schema
    def validate_all(self, data, **kwargs):
        RequestValidator.validate_request_data(data)

# class EmergencyRequestSchema(Schema):
#     """Emergency request schema"""
#     patient_name = fields.Str(required=True)
#     blood_type_needed = fields.Str(required=True)
#     units_needed = fields.Int(load_default=1, validate=validate.Range(min=1, max=10))
#     requester_name = fields.Str(required=True)
#     requester_phone = fields.Str(required=True)
#     requester_latitude = fields.Float(required=True)
#     requester_longitude = fields.Float(required=True)
#     hospital_name = fields.Str(allow_none=True)
    
#     @validates_schema
#     def validate_all(self, data, **kwargs):
#         RequestValidator.validate_emergency_request(data)
# In the EmergencyRequestSchema class (around line 205)
class EmergencyRequestSchema(Schema):
    """Emergency request schema"""
    patient_name = fields.Str(required=True)
    blood_type_needed = fields.Str(required=True)
    units_needed = fields.Int(load_default=1, validate=validate.Range(min=1, max=10))  # Fixed
    requester_name = fields.Str(required=True)
    requester_phone = fields.Str(required=True)
    requester_latitude = fields.Float(required=True)
    requester_longitude = fields.Float(required=True)
    hospital_name = fields.Str(allow_none=True)
    
    @validates_schema
    def validate_all(self, data, **kwargs):
        RequestValidator.validate_emergency_request(data)

import re