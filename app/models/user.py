"""
User Model
"""

from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

@login_manager.user_loader
def load_user(user_id):
    """Flask-Login user loader"""
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    """User model for authentication and common fields"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    role = db.Column(db.String(20), default='donor')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    donor_profile = db.relationship('Donor', back_populates='user',  # This must match the relationship name in Donor
        uselist=False, 
        cascade='all, delete-orphan'
    )
    
    donations_list = db.relationship(
        'Donation', 
        back_populates='donor',
        foreign_keys='Donation.donor_id',
        lazy='dynamic'
    )
    
    requests_list = db.relationship(
        'BloodRequest', 
        back_populates='requester',
        foreign_keys='BloodRequest.requester_id',
        lazy='dynamic'
    )
    
    admin_log_entries = db.relationship(
        'AdminLog',
        back_populates='admin',
        foreign_keys='AdminLog.admin_id',
        lazy='dynamic'
    )
    
    verified_donations_list = db.relationship(
        'Donation',
        back_populates='verifier',
        foreign_keys='Donation.verified_by',
        lazy='dynamic'
    )
    
    def set_password(self, password):
        """Hash and set password"""
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password, password)
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def is_admin(self):
        """Check if user is admin"""
        return self.role == 'admin'
    
    def is_donor(self):
        """Check if user is donor"""
        return self.role == 'donor'
    
    def get_donations(self):
        """Get all donations made by this user"""
        return self.donations_list.all()
    
    def get_donor_profile(self):
        """Get donor profile if exists"""
        return self.donor_profile
    
    def __repr__(self):
        return f'<User {self.email}>'