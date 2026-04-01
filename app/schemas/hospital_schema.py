"""
Hospital Schema - Serialization for Hospital model
"""

from marshmallow import Schema, fields, validate, post_load
from app.models.hospital import Hospital

class HospitalSchema(Schema):
    """Hospital schema for serialization"""
    
    id = fields.Int(dump_only=True)
    hospital_id = fields.Str(dump_only=True)
    
    # Basic Information
    name = fields.Str(required=True)
    registration_number = fields.Str(allow_none=True)
    license_number = fields.Str(allow_none=True)
    
    # Contact
    phone = fields.Str(required=True, validate=validate.Length(10, 20))
    email = fields.Email(allow_none=True)
    emergency_phone = fields.Str(allow_none=True, validate=validate.Length(10, 20))
    website = fields.Url(allow_none=True)
    
    # Address
    address = fields.Str(required=True)
    city = fields.Str(required=True)
    state = fields.Str(required=True)
    pincode = fields.Str(required=True, validate=validate.Length(6, 10))
    
    # Location
    latitude = fields.Float(required=True)
    longitude = fields.Float(required=True)
    
    # Type and Status
    hospital_type = fields.Str(allow_none=True)
    has_blood_bank = fields.Bool(default=False)
    is_verified = fields.Bool(dump_only=True)
    
    # Contact Person
    contact_person_name = fields.Str(allow_none=True)
    contact_person_designation = fields.Str(allow_none=True)
    contact_person_phone = fields.Str(allow_none=True, validate=validate.Length(10, 20))
    
    # Timestamps
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    # Computed fields
    distance_km = fields.Float(dump_only=True)
    
    class Meta:
        ordered = True
    
    @post_load
    def make_hospital(self, data, **kwargs):
        """Create Hospital instance from data"""
        return Hospital(**data)

class HospitalDetailSchema(HospitalSchema):
    """Detailed hospital schema"""
    
    recent_requests = fields.Nested('RequestSchema', many=True, dump_only=True)
    
    class Meta:
        ordered = True

class HospitalCreateSchema(Schema):
    """Schema for creating a new hospital"""
    
    name = fields.Str(required=True)
    phone = fields.Str(required=True, validate=validate.Length(10, 20))
    email = fields.Email(allow_none=True)
    address = fields.Str(required=True)
    city = fields.Str(required=True)
    state = fields.Str(required=True)
    pincode = fields.Str(required=True, validate=validate.Length(6, 10))
    latitude = fields.Float(required=True)
    longitude = fields.Float(required=True)
    hospital_type = fields.Str()
    has_blood_bank = fields.Bool()
    contact_person_name = fields.Str()
    contact_person_phone = fields.Str(validate=validate.Length(10, 20))
    registration_number = fields.Str()
    license_number = fields.Str()
    emergency_phone = fields.Str(validate=validate.Length(10, 20))
    website = fields.Url()

class HospitalUpdateSchema(Schema):
    """Schema for updating a hospital"""
    
    name = fields.Str()
    phone = fields.Str(validate=validate.Length(10, 20))
    email = fields.Email()
    address = fields.Str()
    city = fields.Str()
    state = fields.Str()
    pincode = fields.Str(validate=validate.Length(6, 10))
    latitude = fields.Float()
    longitude = fields.Float()
    hospital_type = fields.Str()
    has_blood_bank = fields.Bool()
    contact_person_name = fields.Str()
    contact_person_phone = fields.Str(validate=validate.Length(10, 20))
    emergency_phone = fields.Str(validate=validate.Length(10, 20))
    website = fields.Url()