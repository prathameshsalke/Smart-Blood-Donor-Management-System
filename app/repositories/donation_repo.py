"""
Donation Repository - Data access for Donation model
"""

from app import db
from app.models.donation import Donation
from typing import Optional, List
from datetime import datetime, timedelta

class DonationRepository:
    """Repository for Donation model operations"""
    
    @staticmethod
    def get_by_id(donation_id: int) -> Optional[Donation]:
        """Get donation by ID"""
        return Donation.query.get(donation_id)
    
    @staticmethod
    def get_by_donation_id(donation_id: str) -> Optional[Donation]:
        """Get donation by custom donation ID"""
        return Donation.query.filter_by(donation_id=donation_id).first()
    
    @staticmethod
    def get_by_donor(donor_id: int) -> List[Donation]:
        """Get donations by donor"""
        return Donation.query.filter_by(donor_id=donor_id).order_by(
            Donation.donation_date.desc()
        ).all()
    
    @staticmethod
    def get_by_request(request_id: int) -> List[Donation]:
        """Get donations by request"""
        return Donation.query.filter_by(request_id=request_id).all()
    
    @staticmethod
    def get_recent_donations(limit: int = 10) -> List[Donation]:
        """Get recent donations"""
        return Donation.query.order_by(
            Donation.donation_date.desc()
        ).limit(limit).all()
    
    @staticmethod
    def get_today_donations() -> List[Donation]:
        """Get today's donations"""
        today = datetime.now().date()
        return Donation.query.filter(
            db.func.date(Donation.donation_date) == today
        ).all()
    
    @staticmethod
    def get_this_month_donations() -> List[Donation]:
        """Get this month's donations"""
        now = datetime.now()
        start_of_month = datetime(now.year, now.month, 1)
        return Donation.query.filter(
            Donation.donation_date >= start_of_month
        ).all()
    
    @staticmethod
    def get_unverified_donations() -> List[Donation]:
        """Get unverified donations"""
        return Donation.query.filter_by(is_verified=False).all()
    
    @staticmethod
    def create(donation_data: dict) -> Donation:
        """Create new donation record"""
        donation = Donation(**donation_data)
        db.session.add(donation)
        db.session.commit()
        return donation
    
    @staticmethod
    def update(donation: Donation, donation_data: dict) -> Donation:
        """Update donation"""
        for key, value in donation_data.items():
            if hasattr(donation, key):
                setattr(donation, key, value)
        db.session.commit()
        return donation
    
    @staticmethod
    def verify(donation: Donation, verifier_id: int) -> Donation:
        """Verify donation"""
        donation.is_verified = True
        donation.verified_by = verifier_id
        donation.verified_at = datetime.utcnow()
        db.session.commit()
        return donation
    
    @staticmethod
    def delete(donation: Donation) -> None:
        """Delete donation"""
        db.session.delete(donation)
        db.session.commit()
    
    @staticmethod
    def count() -> int:
        """Count total donations"""
        return Donation.query.count()
    
    @staticmethod
    def count_verified() -> int:
        """Count verified donations"""
        return Donation.query.filter_by(is_verified=True).count()
    
    @staticmethod
    def count_by_blood_type() -> dict:
        """Count donations by blood type"""
        result = {}
        blood_types = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        
        for bt in blood_types:
            count = Donation.query.filter_by(donor_blood_type=bt).count()
            result[bt] = count
        
        return result
    
    @staticmethod
    def get_donations_by_date_range(start_date: datetime, end_date: datetime) -> List[Donation]:
        """Get donations within date range"""
        return Donation.query.filter(
            Donation.donation_date.between(start_date, end_date)
        ).all()