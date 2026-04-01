"""
User Schema - Serialization for User model
"""

from marshmallow import Schema, fields, validate, post_load, validates_schema, ValidationError
from app.models.user import User

class UserSchema(Schema):
    """User schema for serialization"""
    
    id = fields.Int(dump_only=True)
    email = fields.Email(required=True)
    name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    phone = fields.Str(required=True, validate=validate.Length(10, 20))
    role = fields.Str(dump_only=True)
    is_active = fields.Bool(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    last_login = fields.DateTime(dump_only=True)
    
    class Meta:
        ordered = True
    
    @post_load
    def make_user(self, data, **kwargs):
        """Create User instance from data"""
        return User(**data)

class UserCreateSchema(Schema):
    """Schema for creating a new user"""
    
    email = fields.Email(required=True)
    name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    phone = fields.Str(required=True, validate=validate.Length(10, 20))
    password = fields.Str(required=True, validate=validate.Length(min=6))
    confirm_password = fields.Str(required=True)
    
    @validates_schema
    def validate_passwords(self, data, **kwargs):
        """Validate password confirmation"""
        if data['password'] != data['confirm_password']:
            raise ValidationError('Passwords do not match')

class UserUpdateSchema(Schema):
    """Schema for updating a user"""
    
    name = fields.Str(validate=validate.Length(min=2, max=100))
    phone = fields.Str(validate=validate.Length(10, 20))
    email = fields.Email()

class UserLoginSchema(Schema):
    """Schema for user login"""
    
    email = fields.Email(required=True)
    password = fields.Str(required=True)

class UserProfileSchema(UserSchema):
    """Detailed user profile schema"""
    
    donor_profile = fields.Nested('DonorSchema', dump_only=True)
    
    class Meta:
        ordered = True