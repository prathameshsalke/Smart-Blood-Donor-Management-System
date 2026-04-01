"""
Blood Request Model
"""

from app import db
from datetime import datetime, timedelta

class BloodRequest(db.Model):
    __tablename__ = 'blood_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.String(20), unique=True, nullable=False)
    
    requester_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    requester_name = db.Column(db.String(100), nullable=False)
    requester_phone = db.Column(db.String(20), nullable=False)
    requester_email = db.Column(db.String(120))
    requester_type = db.Column(db.String(20))
    
    patient_name = db.Column(db.String(100), nullable=False)
    patient_age = db.Column(db.Integer)
    patient_gender = db.Column(db.String(10))
    blood_type_needed = db.Column(db.String(5), nullable=False)
    units_needed = db.Column(db.Integer, default=1)
    
    hospital_name = db.Column(db.String(100))
    hospital_address = db.Column(db.String(200))
    hospital_latitude = db.Column(db.Float)
    hospital_longitude = db.Column(db.Float)
    
    urgency = db.Column(db.String(20), default='medium')
    status = db.Column(db.String(20), default='pending')
    reason = db.Column(db.Text)
    required_by_date = db.Column(db.Date)
    
    requester_latitude = db.Column(db.Float, nullable=False)
    requester_longitude = db.Column(db.Float, nullable=False)
    search_radius = db.Column(db.Integer, default=10)
    
    notified_donors = db.Column(db.Integer, default=0)
    accepted_donors = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    fulfilled_at = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)
    
    # Relationships
    requester = db.relationship('User', foreign_keys=[requester_id], back_populates='requests_list')
    donations = db.relationship('Donation', foreign_keys='Donation.request_id', back_populates='blood_request', lazy='dynamic')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.request_id:
            self.request_id = self.generate_request_id()
        if not self.expires_at:
            if self.urgency == 'emergency':
                self.expires_at = datetime.utcnow() + timedelta(hours=48)
            else:
                self.expires_at = datetime.utcnow() + timedelta(days=7)
    
    @staticmethod
    def generate_request_id():
        import random
        import string
        timestamp = datetime.now().strftime('%Y%m%d')
        random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        return f"REQ{timestamp}{random_chars}"
    
    def is_emergency(self):
        return self.urgency == 'emergency'
    
    def can_accept_donations(self):
        if self.status != 'pending':
            return False
        if self.expires_at and self.expires_at < datetime.utcnow():
            self.status = 'expired'
            db.session.commit()
            return False
        return self.accepted_donors < self.units_needed
    
    def mark_fulfilled(self):
        self.status = 'fulfilled'
        self.fulfilled_at = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self):
        return {
            'request_id': self.request_id,
            'patient_name': self.patient_name,
            'blood_type': self.blood_type_needed,
            'units': self.units_needed,
            'urgency': self.urgency,
            'hospital': self.hospital_name,
            'latitude': self.requester_latitude,
            'longitude': self.requester_longitude,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'status': self.status
        }
    
    def __repr__(self):
        return f'<BloodRequest {self.request_id}>'