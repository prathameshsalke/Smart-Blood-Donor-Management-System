"""
Donor Repository - Data access for Donor model
"""

from app import db
from app.models.donor import Donor
from app.models.user import User
from typing import Optional, List
from datetime import datetime, timedelta

class DonorRepository:
    """Repository for Donor model operations"""
    
    @staticmethod
    def get_by_id(donor_id: int) -> Optional[Donor]:
        """Get donor by ID"""
        return Donor.query.get(donor_id)
    
    @staticmethod
    def get_by_user_id(user_id: int) -> Optional[Donor]:
        """Get donor by user ID"""
        return Donor.query.filter_by(user_id=user_id).first()
    
    @staticmethod
    def get_by_blood_type(blood_type: str) -> List[Donor]:
        """Get donors by blood type"""
        return Donor.query.join(User).filter(
            Donor.blood_type == blood_type,
            User.is_active == True
        ).all()
    
    @staticmethod
    def get_eligible_donors() -> List[Donor]:
        """Get all eligible donors"""
        return Donor.query.join(User).filter(
            Donor.is_eligible == True,
            Donor.is_available == True,
            User.is_active == True
        ).all()
    
    @staticmethod
    def get_available_donors() -> List[Donor]:
        """Get all available donors"""
        return Donor.query.join(User).filter(
            Donor.is_available == True,
            User.is_active == True
        ).all()
    
    @staticmethod
    def get_recent_donors(limit: int = 10) -> List[Donor]:
        """Get recently registered donors"""
        return Donor.query.join(User).filter(
            User.is_active == True
        ).order_by(Donor.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def get_donors_with_location() -> List[Donor]:
        """Get donors with location data"""
        return Donor.query.filter(
            Donor.latitude.isnot(None),
            Donor.longitude.isnot(None)
        ).all()
    
    @staticmethod
    def create(donor_data: dict) -> Donor:
        """Create new donor profile"""
        donor = Donor(**donor_data)
        db.session.add(donor)
        db.session.commit()
        return donor
    
    @staticmethod
    def update(donor: Donor, donor_data: dict) -> Donor:
        """Update donor profile"""
        for key, value in donor_data.items():
            if hasattr(donor, key):
                setattr(donor, key, value)
        
        # Update eligibility
        donor.update_eligibility()
        db.session.commit()
        return donor
    
    @staticmethod
    def update_location(donor: Donor, latitude: float, longitude: float) -> Donor:
        """Update donor location"""
        donor.latitude = latitude
        donor.longitude = longitude
        donor.location_updated_at = datetime.utcnow()
        db.session.commit()
        return donor
    
    @staticmethod
    def update_availability(donor: Donor, is_available: bool) -> Donor:
        """Update donor availability"""
        donor.is_available = is_available
        db.session.commit()
        return donor
    
    @staticmethod
    def record_donation(donor: Donor) -> Donor:
        """Record a donation"""
        donor.last_donation_date = datetime.utcnow()
        donor.total_donations += 1
        donor.update_eligibility()
        db.session.commit()
        return donor
    
    @staticmethod
    def count() -> int:
        """Count total donors"""
        return Donor.query.count()
    
    @staticmethod
    def count_by_blood_type() -> dict:
        """Count donors by blood type"""
        result = {}
        blood_types = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        
        for bt in blood_types:
            count = Donor.query.filter_by(blood_type=bt).count()
            result[bt] = count
        
        return result
    
    @staticmethod
    def count_eligible() -> int:
        """Count eligible donors"""
        return Donor.query.filter_by(is_eligible=True).count()
    
    @staticmethod
    def search(query: str) -> List[Donor]:
        """Search donors by name, city, or blood type"""
        search_term = f"%{query}%"
        return Donor.query.join(User).filter(
            User.is_active == True,
            (
                User.name.ilike(search_term) |
                Donor.city.ilike(search_term) |
                Donor.blood_type.ilike(search_term)
            )
        ).all()