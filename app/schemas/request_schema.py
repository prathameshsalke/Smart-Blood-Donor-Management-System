"""
Request Schema - Serialization for BloodRequest model
"""

from marshmallow import Schema, fields, validate, post_load, pre_load
from app.models.blood_request import BloodRequest
from datetime import datetime

class RequestSchema(Schema):
    """Blood request schema for serialization"""
    
    id = fields.Int(dump_only=True)
    request_id = fields.Str(dump_only=True)
    
    # Requester Information
    requester_id = fields.Int(allow_none=True)
    requester_name = fields.Str(required=True)
    requester_phone = fields.Str(required=True, validate=validate.Length(10, 20))
    requester_email = fields.Email(allow_none=True)
    requester_type = fields.Str(validate=validate.OneOf(['patient', 'hospital', 'relative']))
    
    # Patient Information
    patient_name = fields.Str(required=True)
    patient_age = fields.Int(allow_none=True, validate=validate.Range(min=0, max=120))
    patient_gender = fields.Str(allow_none=True, validate=validate.OneOf(['male', 'female', 'other']))
    blood_type_needed = fields.Str(required=True, validate=validate.OneOf([
        'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'
    ]))
    units_needed = fields.Int(default=1, validate=validate.Range(min=1, max=10))
    
    # Hospital Information
    hospital_name = fields.Str(allow_none=True)
    hospital_address = fields.Str(allow_none=True)
    hospital_latitude = fields.Float(allow_none=True)
    hospital_longitude = fields.Float(allow_none=True)
    
    # Request Details
    urgency = fields.Str(default='medium', validate=validate.OneOf(['low', 'medium', 'high', 'emergency']))
    status = fields.Str(dump_only=True)
    reason = fields.Str(allow_none=True)
    required_by_date = fields.Date(allow_none=True)
    
    # Location for search
    requester_latitude = fields.Float(required=True)
    requester_longitude = fields.Float(required=True)
    search_radius = fields.Int(default=10)
    
    # Statistics
    notified_donors = fields.Int(dump_only=True)
    accepted_donors = fields.Int(dump_only=True)
    
    # Timestamps
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    fulfilled_at = fields.DateTime(dump_only=True)
    expires_at = fields.DateTime(dump_only=True)
    
    # Computed fields
    is_expired = fields.Method('check_expired', dump_only=True)
    time_remaining = fields.Method('get_time_remaining', dump_only=True)
    
    class Meta:
        ordered = True
    
    def check_expired(self, obj):
        """Check if request is expired"""
        if obj.expires_at:
            return obj.expires_at < datetime.utcnow()
        return False
    
    def get_time_remaining(self, obj):
        """Get time remaining as human readable string"""
        if not obj.expires_at or obj.expires_at < datetime.utcnow():
            return "Expired"
        
        diff = obj.expires_at - datetime.utcnow()
        hours = diff.seconds // 3600
        minutes = (diff.seconds % 3600) // 60
        
        if diff.days > 0:
            return f"{diff.days} days {hours} hours"
        elif hours > 0:
            return f"{hours} hours {minutes} minutes"
        else:
            return f"{minutes} minutes"
    
    @post_load
    def make_request(self, data, **kwargs):
        """Create BloodRequest instance from data"""
        return BloodRequest(**data)

class EmergencyRequestSchema(Schema):
    """Emergency request schema (simplified for quick submission)"""
    
    patient_name = fields.Str(required=True)
    blood_type_needed = fields.Str(required=True, validate=validate.OneOf([
        'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'
    ]))
    units_needed = fields.Int(default=1, validate=validate.Range(min=1, max=10))
    requester_name = fields.Str(required=True)
    requester_phone = fields.Str(required=True, validate=validate.Length(10, 20))
    requester_latitude = fields.Float(required=True)
    requester_longitude = fields.Float(required=True)
    hospital_name = fields.Str(allow_none=True)
    
    @pre_load
    def set_emergency(self, data, **kwargs):
        """Set urgency to emergency"""
        data['urgency'] = 'emergency'
        return data

class RequestUpdateSchema(Schema):
    """Schema for updating a request"""
    
    status = fields.Str(validate=validate.OneOf(['pending', 'fulfilled', 'cancelled']))
    urgency = fields.Str(validate=validate.OneOf(['low', 'medium', 'high', 'emergency']))
    units_needed = fields.Int(validate=validate.Range(min=1, max=10))
    hospital_name = fields.Str()
    required_by_date = fields.Date()

class RequestSearchSchema(Schema):
    """Schema for request search parameters"""
    
    blood_type = fields.Str(validate=validate.OneOf([
        'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'
    ]))
    urgency = fields.Str(validate=validate.OneOf(['low', 'medium', 'high', 'emergency']))
    status = fields.Str(validate=validate.OneOf(['pending', 'fulfilled', 'cancelled']))
    latitude = fields.Float()
    longitude = fields.Float()
    radius = fields.Int(default=10)
    days = fields.Int(default=7)