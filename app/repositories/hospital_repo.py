"""
Hospital Repository - Data access for Hospital model
"""

from app import db
from app.models.hospital import Hospital
from typing import Optional, List

class HospitalRepository:
    """Repository for Hospital model operations"""
    
    @staticmethod
    def get_by_id(hospital_id: int) -> Optional[Hospital]:
        """Get hospital by ID"""
        return Hospital.query.get(hospital_id)
    
    @staticmethod
    def get_by_hospital_id(hospital_id: str) -> Optional[Hospital]:
        """Get hospital by custom hospital ID"""
        return Hospital.query.filter_by(hospital_id=hospital_id).first()
    
    @staticmethod
    def get_by_name(name: str) -> Optional[Hospital]:
        """Get hospital by name"""
        return Hospital.query.filter_by(name=name).first()
    
    @staticmethod
    def get_all() -> List[Hospital]:
        """Get all hospitals"""
        return Hospital.query.all()
    
    @staticmethod
    def get_all_verified() -> List[Hospital]:
        """Get all verified hospitals"""
        return Hospital.query.filter_by(is_verified=True).all()
    
    @staticmethod
    def get_with_blood_bank() -> List[Hospital]:
        """Get hospitals with blood bank"""
        return Hospital.query.filter_by(has_blood_bank=True, is_verified=True).all()
    
    @staticmethod
    def get_by_city(city: str) -> List[Hospital]:
        """Get hospitals by city"""
        return Hospital.query.filter_by(city=city, is_verified=True).all()
    
    @staticmethod
    def get_hospitals_with_location() -> List[Hospital]:
        """Get hospitals with location data"""
        return Hospital.query.filter(
            Hospital.latitude.isnot(None),
            Hospital.longitude.isnot(None)
        ).all()
    
    @staticmethod
    def create(hospital_data: dict) -> Hospital:
        """Create new hospital"""
        hospital = Hospital(**hospital_data)
        db.session.add(hospital)
        db.session.commit()
        return hospital
    
    @staticmethod
    def update(hospital: Hospital, hospital_data: dict) -> Hospital:
        """Update hospital"""
        for key, value in hospital_data.items():
            if hasattr(hospital, key):
                setattr(hospital, key, value)
        db.session.commit()
        return hospital
    
    @staticmethod
    def verify(hospital: Hospital) -> Hospital:
        """Verify hospital"""
        hospital.is_verified = True
        db.session.commit()
        return hospital
    
    @staticmethod
    def delete(hospital: Hospital) -> None:
        """Delete hospital"""
        db.session.delete(hospital)
        db.session.commit()
    
    @staticmethod
    def search(query: str) -> List[Hospital]:
        """Search hospitals by name or city"""
        search_term = f"%{query}%"
        return Hospital.query.filter(
            (Hospital.name.ilike(search_term)) |
            (Hospital.city.ilike(search_term)) |
            (Hospital.address.ilike(search_term))
        ).all()
    
    @staticmethod
    def count() -> int:
        """Count total hospitals"""
        return Hospital.query.count()
    
    @staticmethod
    def count_verified() -> int:
        """Count verified hospitals"""
        return Hospital.query.filter_by(is_verified=True).count()