# """
# Donor Model - Fixed Version
# """

# from app import db
# from datetime import datetime, timedelta
# from sqlalchemy import event

# class Donor(db.Model):
#     """Donor profile model"""
#     __tablename__ = 'donors'
    
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    
#     # Personal Information
#     blood_type = db.Column(db.String(5), nullable=False)
#     date_of_birth = db.Column(db.Date, nullable=False)
#     gender = db.Column(db.String(10), nullable=False)
#     weight = db.Column(db.Float, nullable=False)
    
#     # Contact Information
#     address = db.Column(db.String(200), nullable=False)
#     city = db.Column(db.String(50), nullable=False)
#     state = db.Column(db.String(50), nullable=False)
#     pincode = db.Column(db.String(10), nullable=False)
    
#     # Location
#     latitude = db.Column(db.Float)
#     longitude = db.Column(db.Float)
#     location_updated_at = db.Column(db.DateTime)
    
#     # Medical Information
#     medical_conditions = db.Column(db.Text)
#     medications = db.Column(db.Text)
#     last_donation_date = db.Column(db.DateTime)
#     total_donations = db.Column(db.Integer, default=0)
    
#     # Status
#     is_available = db.Column(db.Boolean, default=True)
#     is_eligible = db.Column(db.Boolean, default=True)
#     eligibility_updated_at = db.Column(db.DateTime)
    
#     # Emergency Contact
#     emergency_contact_name = db.Column(db.String(100))
#     emergency_contact_phone = db.Column(db.String(20))
#     emergency_contact_relation = db.Column(db.String(50))
    
#     # Timestamps
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#     updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

#     #Profile photo
#     profile_photo = db.Column(db.String(200), default='default-avatar.png',nullable=True)
    
#     # Relationship - This MUST match what you use in your code
#     # If your code uses 'user', then the backref should be 'user'
#     user = db.relationship('User', back_populates='donor_profile', uselist=False)
    
#     @property
#     def donation_history(self):
#         """Get donation history through the associated user"""
#         if self.user:
#             return self.user.donations_list
#         return []
    
#     def calculate_age(self):
#         """Calculate donor's age"""
#         today = datetime.now().date()
#         age = today.year - self.date_of_birth.year
#         if today.month < self.date_of_birth.month or \
#            (today.month == self.date_of_birth.month and today.day < self.date_of_birth.day):
#             age -= 1
#         return age
    
#     def check_eligibility(self):
#         """Check if donor is eligible to donate"""
#         if not self.is_available:
#             return False, "Donor is marked as unavailable"
        
#         if self.calculate_age() < 18 or self.calculate_age() > 65:
#             return False, f"Donor age {self.calculate_age()} must be between 18 and 65 years"
        
#         if self.weight < 45:
#             return False, f"Donor weight {self.weight} kg must be at least 45 kg"
        
#         if self.last_donation_date:
#             days_since_last = (datetime.now() - self.last_donation_date).days
#             if days_since_last < 90:
#                 return False, f"Must wait {90 - days_since_last} more days"
        
#         return True, "Donor is eligible"
    
#     def update_eligibility(self):
#         """Update eligibility status"""
#         is_eligible, message = self.check_eligibility()
#         self.is_eligible = is_eligible
#         self.eligibility_updated_at = datetime.utcnow()
#         return is_eligible, message
    
#     def get_next_eligible_date(self):
#         """Calculate next eligible donation date"""
#         if not self.last_donation_date:
#             return datetime.now().date()
#         return (self.last_donation_date + timedelta(days=90)).date()
    
#     def get_donations(self):
#         """Get all donations for this donor"""
#         if self.user:
#             return self.user.donations_list.all()
#         return []
    
#     def to_dict(self):
#         """Convert donor to dictionary for API"""
#         return {
#             'id': self.id,
#             'name': self.user.name if self.user else None,  # Using 'user' not 'user'
#             'blood_type': self.blood_type,
#             'age': self.calculate_age(),
#             'city': self.city,
#             'state': self.state,
#             'phone': self.user.phone if self.user else None,  # Using 'user' not 'user'
#             'latitude': self.latitude,
#             'longitude': self.longitude,
#             'is_eligible': self.is_eligible,
#             'is_available': self.is_available,
#             'total_donations': self.total_donations,
#             'last_donation_date': self.last_donation_date.isoformat() if self.last_donation_date else None
#         }
    
#     def __repr__(self):
#         return f'<Donor {self.user_id} - {self.blood_type}>'

# # Event listener to update eligibility on save
# @event.listens_for(Donor, 'before_insert')
# @event.listens_for(Donor, 'before_update')
# def update_eligibility_on_save(mapper, connection, target):
#     """Automatically update eligibility before saving"""
#     target.update_eligibility()



"""
Donor Model - Fixed Version with Photo Support
"""

from app import db
from datetime import datetime, timedelta
from sqlalchemy import event
import random
import string


class Donor(db.Model):
    """Donor profile model"""
    __tablename__ = 'donors'
    
    id = db.Column(db.Integer, primary_key=True)
    donor_unique_id = db.Column(db.String(20), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    
    # Personal Information
    blood_type = db.Column(db.String(5), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    weight = db.Column(db.Float, nullable=False)
    
    # Contact Information
    address = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    pincode = db.Column(db.String(10), nullable=False)
    
    # Location
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    location_updated_at = db.Column(db.DateTime)
    
    # Medical Information
    medical_conditions = db.Column(db.Text)
    medications = db.Column(db.Text)
    last_donation_date = db.Column(db.DateTime)
    total_donations = db.Column(db.Integer, default=0)
    
    # Status
    is_available = db.Column(db.Boolean, default=True)
    is_eligible = db.Column(db.Boolean, default=True)
    eligibility_updated_at = db.Column(db.DateTime)
    
    # Emergency Contact
    emergency_contact_name = db.Column(db.String(100))
    emergency_contact_phone = db.Column(db.String(20))
    emergency_contact_relation = db.Column(db.String(50))
    
    # Additional Information
    nationality = db.Column(db.String(50), nullable=False, default='Indian')
    has_disability = db.Column(db.Boolean, default=False)
    disability = db.Column(db.String(200), nullable=True)
    
    # Profile Photo - FIXED: Use consistent field name
    profile_photo = db.Column(db.String(200), nullable=True, default=None)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', back_populates='donor_profile', uselist=False)


    def __init__(self, *args, **kwargs):
        # Generate unique donor ID before initialization
        if 'donor_unique_id' not in kwargs or not kwargs['donor_unique_id']:
            kwargs['donor_unique_id'] = self.generate_unique_id()
        super().__init__(*args, **kwargs)
    
    @staticmethod
    def generate_unique_id():
        """Generate unique donor ID with format: DNR + timestamp + random chars"""
        timestamp = datetime.now().strftime('%y%m%d%H%M')
        random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        # Format: DNR2402191530A7B9 (DNR + YYMMDDHHMM + 4 random chars)
        return f"DNR{timestamp}{random_chars}"
    
    @property
    def donation_history(self):
        """Get donation history through the associated user"""
        if self.user:
            return self.user.donations_list
        return []
    
    @property
    def profile_photo_url(self):
        """Get profile photo URL or default"""
        if self.profile_photo:
            return f"uploads/profiles/{self.profile_photo}"
        return "images/default-avatar.png"
    
    def calculate_age(self):
        """Calculate donor's age"""
        today = datetime.now().date()
        age = today.year - self.date_of_birth.year
        if today.month < self.date_of_birth.month or \
           (today.month == self.date_of_birth.month and today.day < self.date_of_birth.day):
            age -= 1
        return age
    
    # def check_eligibility(self):
    #     """Check if donor is eligible to donate"""
    #     if not self.is_available:
    #         return False, "Donor is marked as unavailable"
        
    #     if self.calculate_age() < 18 or self.calculate_age() > 65:
    #         return False, f"Donor age {self.calculate_age()} must be between 18 and 65 years"
        
    #     if self.weight < 45:
    #         return False, f"Donor weight {self.weight} kg must be at least 45 kg"
        
    #     if self.last_donation_date:
    #         days_since_last = (datetime.now() - self.last_donation_date).days
    #         if days_since_last < 90:
    #             return False, f"Must wait {90 - days_since_last} more days"
        
    #     return True, "Donor is eligible"

    def check_eligibility(self):
        """Check if donor is eligible to donate"""
        if not self.is_available:
           return False, "Donor is marked as unavailable", None
    
        if self.calculate_age() < 18 or self.calculate_age() > 65:
           return False, f"Donor age {self.calculate_age()} must be between 18 and 65 years", None
    
        if self.weight < 45:
          return False, f"Donor weight {self.weight} kg must be at least 45 kg", None
    
        if self.last_donation_date:
           days_since_last = (datetime.now() - self.last_donation_date).days
           if days_since_last < 90:
              next_date = self.last_donation_date + timedelta(days=90)
              return False, f"Must wait {90 - days_since_last} more days", next_date.date()
    
        return True, "Donor is eligible", None
    
    # def update_eligibility(self):
    #     """Update eligibility status"""
    #     is_eligible, message = self.check_eligibility()
    #     self.is_eligible = is_eligible
    #     self.eligibility_updated_at = datetime.utcnow()
    #     return is_eligible, message
    
    def update_eligibility(self):
        """
        Update eligibility status
        Returns: (is_eligible, message)
        """
        is_eligible, message, next_date = self.check_eligibility()
        self.is_eligible = is_eligible
        self.eligibility_updated_at = datetime.utcnow()
        return is_eligible, message
    
    def get_next_eligible_date(self):
        """Calculate next eligible donation date"""
        if not self.last_donation_date:
            return datetime.now().date()
        return (self.last_donation_date + timedelta(days=90)).date()
    
    def get_donations(self):
        """Get all donations for this donor"""
        if self.user:
            return self.user.donations_list.all()
        return []
    
    def to_dict(self):
        """Convert donor to dictionary for API"""
        return {
            'id': self.id,
            'donor_unique_id': self.donor_unique_id,
            'name': self.user.name if self.user else None,
            'blood_type': self.blood_type,
            'age': self.calculate_age(),
            'city': self.city,
            'state': self.state,
            'phone': self.user.phone if self.user else None,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'is_eligible': self.is_eligible,
            'is_available': self.is_available,
            'total_donations': self.total_donations,
            'last_donation_date': self.last_donation_date.isoformat() if self.last_donation_date else None,
            'profile_photo': self.profile_photo,
            'nationality': self.nationality,
            'has_disability': self.has_disability,
            'disability': self.disability
        }
    
    def __repr__(self):
        return f'<Donor {self.user_id} - {self.blood_type}>'

# Event listener to update eligibility on save
@event.listens_for(Donor, 'before_insert')
@event.listens_for(Donor, 'before_update')
def update_eligibility_on_save(mapper, connection, target):
    """Automatically update eligibility before saving"""
    target.update_eligibility()