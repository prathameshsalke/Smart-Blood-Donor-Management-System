"""
Message Model for donor notifications and messages
"""

from app import db
from datetime import datetime

class Message(db.Model):
    """Message model for donor notifications"""
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.String(20), unique=True, nullable=False)
    
    # Recipient and Sender
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Message Details
    subject = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(50), default='notification')  # notification, certificate, request, system
    
    # Status
    is_read = db.Column(db.Boolean, default=False)
    read_at = db.Column(db.DateTime)
    is_archived = db.Column(db.Boolean, default=False)
    
    # Related entities
    related_donation_id = db.Column(db.String(20), nullable=True)
    related_request_id = db.Column(db.String(20), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    recipient = db.relationship('User', foreign_keys=[recipient_id], backref='received_messages')
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.message_id:
            self.message_id = self.generate_message_id()
    
    @staticmethod
    def generate_message_id():
        """Generate unique message ID"""
        import random
        import string
        timestamp = datetime.now().strftime('%y%m%d%H%M%S')
        random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return f"MSG{timestamp}{random_chars}"
    
    def mark_as_read(self):
        """Mark message as read"""
        self.is_read = True
        self.read_at = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.message_id,
            'subject': self.subject,
            'content': self.content,
            'type': self.message_type,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat(),
            'read_at': self.read_at.isoformat() if self.read_at else None
        }
    
    def __repr__(self):
        return f'<Message {self.message_id} to {self.recipient_id}>'