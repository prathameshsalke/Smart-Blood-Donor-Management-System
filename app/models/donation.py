"""
Donation Model
"""

from app import db
from datetime import datetime
import uuid

class Donation(db.Model):
    """Blood donation record model"""
    __tablename__ = 'donations'
    
    id = db.Column(db.Integer, primary_key=True)
    donation_id = db.Column(db.String(20), unique=True, nullable=False)
    
    # Donor Information
    donor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    donor_name = db.Column(db.String(100), nullable=False)
    donor_blood_type = db.Column(db.String(5), nullable=False)
    
    # Request Information
    request_id = db.Column(db.Integer, db.ForeignKey('blood_requests.id'), nullable=True)
    request_ref = db.Column(db.String(20))
    
    # Donation Details
    donation_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    units_donated = db.Column(db.Integer, default=1)
    blood_pressure = db.Column(db.String(20))
    hemoglobin_level = db.Column(db.Float)
    notes = db.Column(db.Text)
    
    # Location
    donation_center = db.Column(db.String(100))
    donation_center_address = db.Column(db.String(200))
    
    # Certificate
    certificate_generated = db.Column(db.Boolean, default=False)
    certificate_path = db.Column(db.String(200))
    qr_code_path = db.Column(db.String(200))
    
    # Status
    is_verified = db.Column(db.Boolean, default=False)
    verified_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    verified_at = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships - Using back_populates
    donor = db.relationship('User', foreign_keys=[donor_id], back_populates='donations_list')
    verifier = db.relationship('User', foreign_keys=[verified_by], back_populates='verified_donations_list')
    blood_request = db.relationship('BloodRequest', foreign_keys=[request_id], back_populates='donations')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.donation_id:
            self.donation_id = self.generate_donation_id()
    
    @staticmethod
    def generate_donation_id():
        """Generate unique donation ID"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        unique_id = str(uuid.uuid4())[:4].upper()
        return f"DON{timestamp}{unique_id}"
    
    def generate_certificate(self):
        """Generate donation certificate"""
        self.certificate_generated = True
        db.session.commit()
        return True
    
# Add these methods to the Donation class

def send_certificate_notification(self):
    """Send certificate notification to donor"""
    from app.models.message import Message
    from app.services.email_service import EmailService
    
    # Create dashboard message
    message = Message(
        recipient_id=self.donor_id,
        subject=f"Donation Certificate Generated - {self.donation_id}",
        content=f"""
        Your blood donation certificate has been generated!
        
        Donation ID: {self.donation_id}
        Date: {self.donation_date.strftime('%B %d, %Y')}
        Units: {self.units_donated}
        
        You can download your certificate from your dashboard.
        """,
        message_type='certificate',
        related_donation_id=self.donation_id
    )
    db.session.add(message)
    
    # Send email notification
    EmailService.send_certificate_notification(self)
    
    db.session.commit()
    
    def to_dict(self):
        """Convert to dictionary for API"""
        return {
            'donation_id': self.donation_id,
            'donor_name': self.donor_name,
            'blood_type': self.donor_blood_type,
            'donation_date': self.donation_date.isoformat(),
            'units': self.units_donated,
            'verified': self.is_verified,
            'certificate': self.certificate_generated,
            'donation_center': self.donation_center
        }
    
    def __repr__(self):
        return f'<Donation {self.donation_id}>'