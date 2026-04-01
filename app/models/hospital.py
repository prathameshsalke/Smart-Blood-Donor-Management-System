"""
Hospital Model for registered hospitals
"""

from app import db
from datetime import datetime

class Hospital(db.Model):
    """Hospital model"""
    __tablename__ = 'hospitals'
    
    id = db.Column(db.Integer, primary_key=True)
    hospital_id = db.Column(db.String(20), unique=True, nullable=False)
    
    # Basic Information
    name = db.Column(db.String(100), nullable=False)
    registration_number = db.Column(db.String(50), unique=True)
    license_number = db.Column(db.String(50))
    
    # Contact Information
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120))
    emergency_phone = db.Column(db.String(20))
    website = db.Column(db.String(100))
    
    # Address
    address = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    pincode = db.Column(db.String(10), nullable=False)
    
    # Location
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    
    # Hospital Type
    hospital_type = db.Column(db.String(50))  # Government, Private, Trust, etc.
    has_blood_bank = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)
    
    # Contact Person
    contact_person_name = db.Column(db.String(100))
    contact_person_designation = db.Column(db.String(50))
    contact_person_phone = db.Column(db.String(20))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.hospital_id:
            self.hospital_id = self.generate_hospital_id()
    
    @staticmethod
    def generate_hospital_id():
        """Generate unique hospital ID"""
        import random
        import string
        timestamp = datetime.now().strftime('%Y%m')
        random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        return f"HOS{timestamp}{random_chars}"
    
    def to_dict(self):
        """Convert to dictionary for API"""
        return {
            'id': self.hospital_id,
            'name': self.name,
            'phone': self.phone,
            'address': self.address,
            'city': self.city,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'type': self.hospital_type,
            'has_blood_bank': self.has_blood_bank
        }
    
    def __repr__(self):
        return f'<Hospital {self.name}>'