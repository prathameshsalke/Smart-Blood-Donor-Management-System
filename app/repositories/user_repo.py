"""
User Repository - Data access for User model
"""

from app import db
from app.models.user import User
from typing import Optional, List

class UserRepository:
    """Repository for User model operations"""
    
    @staticmethod
    def get_by_id(user_id: int) -> Optional[User]:
        """Get user by ID"""
        return User.query.get(user_id)
    
    @staticmethod
    def get_by_email(email: str) -> Optional[User]:
        """Get user by email"""
        return User.query.filter_by(email=email).first()
    
    @staticmethod
    def get_by_phone(phone: str) -> Optional[User]:
        """Get user by phone"""
        return User.query.filter_by(phone=phone).first()
    
    @staticmethod
    def get_all_active() -> List[User]:
        """Get all active users"""
        return User.query.filter_by(is_active=True).all()
    
    @staticmethod
    def get_all_donors() -> List[User]:
        """Get all donor users"""
        return User.query.filter_by(role='donor', is_active=True).all()
    
    @staticmethod
    def get_all_admins() -> List[User]:
        """Get all admin users"""
        return User.query.filter_by(role='admin', is_active=True).all()
    
    @staticmethod
    def create(user_data: dict) -> User:
        """Create new user"""
        user = User(**user_data)
        db.session.add(user)
        db.session.commit()
        return user
    
    @staticmethod
    def update(user: User, user_data: dict) -> User:
        """Update user"""
        for key, value in user_data.items():
            if hasattr(user, key):
                setattr(user, key, value)
        db.session.commit()
        return user
    
    @staticmethod
    def delete(user: User) -> None:
        """Delete user (soft delete by deactivating)"""
        user.is_active = False
        db.session.commit()
    
    @staticmethod
    def hard_delete(user: User) -> None:
        """Permanently delete user"""
        db.session.delete(user)
        db.session.commit()
    
    @staticmethod
    def authenticate(email: str, password: str) -> Optional[User]:
        """Authenticate user"""
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password) and user.is_active:
            return user
        return None
    
    @staticmethod
    def count() -> int:
        """Count total users"""
        return User.query.count()
    
    @staticmethod
    def count_active() -> int:
        """Count active users"""
        return User.query.filter_by(is_active=True).count()