"""
Donor Schema - Serialization for Donor model
"""

from marshmallow import Schema, fields, validate, post_load, pre_dump
from app.models.donor import Donor
from datetime import datetime

class DonorSchema(Schema):
    """Donor schema for serialization"""
    
    # Basic fields
    id = fields.Int(dump_only=True)
    user_id = fields.Int(required=True)
    
    # Personal Information
    name = fields.Str(attribute='user.name', dump_only=True)
    email = fields.Str(attribute='user.email', dump_only=True)
    phone = fields.Str(attribute='user.phone', dump_only=True)
    blood_type = fields.Str(required=True, validate=validate.OneOf([
        'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'
    ]))
    date_of_birth = fields.Date(required=True)
    age = fields.Method('calculate_age', dump_only=True)
    gender = fields.Str(required=True, validate=validate.OneOf(['male', 'female', 'other']))
    weight = fields.Float(required=True, validate=validate.Range(min=30, max=200))
    
    # Contact Information
    address = fields.Str(required=True)
    city = fields.Str(required=True)
    state = fields.Str(required=True)
    pincode = fields.Str(required=True, validate=validate.Length(6, 10))
    
    # Location
    latitude = fields.Float(allow_none=True)
    longitude = fields.Float(allow_none=True)
    location_updated_at = fields.DateTime(dump_only=True)
    
    # Medical Information
    medical_conditions = fields.Str(allow_none=True)
    medications = fields.Str(allow_none=True)
    last_donation_date = fields.DateTime(dump_only=True)
    total_donations = fields.Int(dump_only=True)
    
    # Status
    is_available = fields.Bool(default=True)
    is_eligible = fields.Bool(dump_only=True)
    eligibility_message = fields.Method('get_eligibility_message', dump_only=True)
    next_eligible_date = fields.Method('get_next_eligible_date', dump_only=True)
    
    # Emergency Contact
    emergency_contact_name = fields.Str(required=True)
    emergency_contact_phone = fields.Str(required=True, validate=validate.Length(10, 20))
    emergency_contact_relation = fields.Str(required=True)
    
    # Timestamps
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    # Computed fields
    distance_km = fields.Float(dump_only=True)  # For nearby searches
    
    class Meta:
        ordered = True
    
    def calculate_age(self, obj):
        """Calculate donor age"""
        if obj.date_of_birth:
            today = datetime.now().date()
            age = today.year - obj.date_of_birth.year
            if today.month < obj.date_of_birth.month or \
               (today.month == obj.date_of_birth.month and today.day < obj.date_of_birth.day):
                age -= 1
            return age
        return None
    
    def get_eligibility_message(self, obj):
        """Get eligibility message"""
        if obj.is_eligible:
            return "Eligible to donate"
        elif obj.last_donation_date:
            from datetime import datetime, timedelta
            next_date = obj.last_donation_date + timedelta(days=90)
            days_left = (next_date - datetime.now()).days
            return f"Will be eligible in {days_left} days"
        return "Not eligible to donate"
    
    def get_next_eligible_date(self, obj):
        """Get next eligible donation date"""
        if obj.last_donation_date:
            from datetime import timedelta
            next_date = obj.last_donation_date + timedelta(days=90)
            return next_date.date()
        return None
    
    @post_load
    def make_donor(self, data, **kwargs):
        """Create Donor instance from data"""
        return Donor(**data)

class DonorDetailSchema(DonorSchema):
    """Detailed donor schema with additional info"""
    
    donation_history = fields.Nested('DonationSchema', many=True, dump_only=True)
    recent_requests = fields.Nested('RequestSchema', many=True, dump_only=True)
    
    class Meta:
        ordered = True

class DonorCreateSchema(Schema):
    """Schema for creating a new donor"""
    
    # Personal Information
    blood_type = fields.Str(required=True, validate=validate.OneOf([
        'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'
    ]))
    date_of_birth = fields.Date(required=True)
    gender = fields.Str(required=True, validate=validate.OneOf(['male', 'female', 'other']))
    weight = fields.Float(required=True, validate=validate.Range(min=30, max=200))
    
    # Contact Information
    address = fields.Str(required=True)
    city = fields.Str(required=True)
    state = fields.Str(required=True)
    pincode = fields.Str(required=True, validate=validate.Length(6, 10))
    
    # Emergency Contact
    emergency_contact_name = fields.Str(required=True)
    emergency_contact_phone = fields.Str(required=True, validate=validate.Length(10, 20))
    emergency_contact_relation = fields.Str(required=True)
    
    # Medical (optional)
    medical_conditions = fields.Str(allow_none=True)
    medications = fields.Str(allow_none=True)

class DonorUpdateSchema(Schema):
    """Schema for updating a donor"""
    
    address = fields.Str()
    city = fields.Str()
    state = fields.Str()
    pincode = fields.Str(validate=validate.Length(6, 10))
    medical_conditions = fields.Str(allow_none=True)
    medications = fields.Str(allow_none=True)
    is_available = fields.Bool()
    emergency_contact_name = fields.Str()
    emergency_contact_phone = fields.Str(validate=validate.Length(10, 20))
    emergency_contact_relation = fields.Str()
    latitude = fields.Float()
    longitude = fields.Float()