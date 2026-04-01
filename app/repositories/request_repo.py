"""
Blood Request Repository - Data access for BloodRequest model
"""

from app import db
from app.models.blood_request import BloodRequest
from typing import Optional, List
from datetime import datetime, timedelta

class BloodRequestRepository:
    """Repository for BloodRequest model operations"""
    
    @staticmethod
    def get_by_id(request_id: int) -> Optional[BloodRequest]:
        """Get request by ID"""
        return BloodRequest.query.get(request_id)
    
    @staticmethod
    def get_by_request_id(request_id: str) -> Optional[BloodRequest]:
        """Get request by custom request ID"""
        return BloodRequest.query.filter_by(request_id=request_id).first()
    
    @staticmethod
    def get_pending_requests() -> List[BloodRequest]:
        """Get all pending requests"""
        return BloodRequest.query.filter_by(status='pending').order_by(
            BloodRequest.created_at.desc()
        ).all()
    
    @staticmethod
    def get_emergency_requests() -> List[BloodRequest]:
        """Get all emergency requests"""
        return BloodRequest.query.filter_by(
            urgency='emergency',
            status='pending'
        ).order_by(BloodRequest.created_at.desc()).all()
    
    @staticmethod
    def get_requests_by_blood_type(blood_type: str) -> List[BloodRequest]:
        """Get requests by blood type"""
        return BloodRequest.query.filter_by(
            blood_type_needed=blood_type,
            status='pending'
        ).order_by(BloodRequest.created_at.desc()).all()
    
    @staticmethod
    def get_recent_requests(limit: int = 10) -> List[BloodRequest]:
        """Get recent requests"""
        return BloodRequest.query.order_by(
            BloodRequest.created_at.desc()
        ).limit(limit).all()
    
    @staticmethod
    def get_requests_by_requester(requester_id: int) -> List[BloodRequest]:
        """Get requests by requester"""
        return BloodRequest.query.filter_by(
            requester_id=requester_id
        ).order_by(BloodRequest.created_at.desc()).all()
    
    @staticmethod
    def create(request_data: dict) -> BloodRequest:
        """Create new blood request"""
        request = BloodRequest(**request_data)
        db.session.add(request)
        db.session.commit()
        return request
    
    @staticmethod
    def create_emergency_request(request_data: dict) -> BloodRequest:
        """Create emergency request"""
        request_data['urgency'] = 'emergency'
        request = BloodRequest(**request_data)
        db.session.add(request)
        db.session.commit()
        return request
    
    @staticmethod
    def update(request: BloodRequest, request_data: dict) -> BloodRequest:
        """Update request"""
        for key, value in request_data.items():
            if hasattr(request, key):
                setattr(request, key, value)
        db.session.commit()
        return request
    
    @staticmethod
    def mark_fulfilled(request: BloodRequest) -> BloodRequest:
        """Mark request as fulfilled"""
        request.status = 'fulfilled'
        request.fulfilled_at = datetime.utcnow()
        db.session.commit()
        return request
    
    @staticmethod
    def mark_expired(request: BloodRequest) -> BloodRequest:
        """Mark request as expired"""
        request.status = 'expired'
        db.session.commit()
        return request
    
    @staticmethod
    def delete(request: BloodRequest) -> None:
        """Delete request"""
        db.session.delete(request)
        db.session.commit()
    
    @staticmethod
    def increment_notified(request: BloodRequest) -> BloodRequest:
        """Increment notified donors count"""
        request.notified_donors += 1
        db.session.commit()
        return request
    
    @staticmethod
    def increment_accepted(request: BloodRequest) -> BloodRequest:
        """Increment accepted donors count"""
        request.accepted_donors += 1
        
        # Check if fulfilled
        if request.accepted_donors >= request.units_needed:
            request.mark_fulfilled()
        
        db.session.commit()
        return request
    
    @staticmethod
    def count() -> dict:
        """Count requests by status"""
        return {
            'total': BloodRequest.query.count(),
            'pending': BloodRequest.query.filter_by(status='pending').count(),
            'fulfilled': BloodRequest.query.filter_by(status='fulfilled').count(),
            'cancelled': BloodRequest.query.filter_by(status='cancelled').count(),
            'expired': BloodRequest.query.filter_by(status='expired').count(),
            'emergency': BloodRequest.query.filter_by(urgency='emergency', status='pending').count()
        }
    
    @staticmethod
    def cleanup_expired() -> int:
        """Mark expired requests and return count"""
        expired = BloodRequest.query.filter(
            BloodRequest.status == 'pending',
            BloodRequest.expires_at < datetime.utcnow()
        ).all()
        
        count = 0
        for request in expired:
            request.status = 'expired'
            count += 1
        
        db.session.commit()
        return count