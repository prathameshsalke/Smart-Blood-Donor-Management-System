"""
Cleanup Tasks - Periodic cleanup jobs
"""

from datetime import datetime, timedelta
from app.repositories.request_repo import BloodRequestRepository
from app.repositories.donation_repo import DonationRepository
from app.services.export_service import ExportService
from app.utils.logger import logger

def cleanup_expired_requests():
    """Mark expired requests and clean up"""
    try:
        # Get expired requests
        from app.models.blood_request import BloodRequest
        from app import db
        
        expired = BloodRequest.query.filter(
            BloodRequest.status == 'pending',
            BloodRequest.expires_at < datetime.utcnow()
        ).all()
        
        count = 0
        for request in expired:
            request.status = 'expired'
            count += 1
        
        db.session.commit()
        logger.info(f"Cleaned up {count} expired requests")
        
        return count
        
    except Exception as e:
        logger.error(f"Error cleaning up expired requests: {str(e)}")
        return 0

def cleanup_old_exports(days=7):
    """Delete old export files"""
    try:
        export_service = ExportService()
        count = export_service.cleanup_old_exports(days)
        logger.info(f"Cleaned up {count} old export files")
        return count
        
    except Exception as e:
        logger.error(f"Error cleaning up exports: {str(e)}")
        return 0

def cleanup_unverified_donations(days=30):
    """Delete old unverified donations"""
    try:
        from app.models.donation import Donation
        from app import db
        
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        unverified = Donation.query.filter(
            Donation.is_verified == False,
            Donation.created_at < cutoff
        ).all()
        
        count = 0
        for donation in unverified:
            # Delete certificate files if any
            if donation.certificate_path:
                import os
                try:
                    if os.path.exists(donation.certificate_path):
                        os.remove(donation.certificate_path)
                except:
                    pass
            
            db.session.delete(donation)
            count += 1
        
        db.session.commit()
        logger.info(f"Cleaned up {count} unverified donations")
        
        return count
        
    except Exception as e:
        logger.error(f"Error cleaning up donations: {str(e)}")
        return 0

def cleanup_inactive_users(days=365):
    """Deactivate users inactive for long time"""
    try:
        from app.models.user import User
        from app import db
        
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        inactive = User.query.filter(
            User.is_active == True,
            User.last_login < cutoff,
            User.role != 'admin'  # Don't deactivate admins
        ).all()
        
        count = 0
        for user in inactive:
            user.is_active = False
            count += 1
        
        db.session.commit()
        logger.info(f"Deactivated {count} inactive users")
        
        return count
        
    except Exception as e:
        logger.error(f"Error cleaning up inactive users: {str(e)}")
        return 0

def cleanup_temp_files(days=1):
    """Clean up temporary files"""
    import os
    import tempfile
    
    try:
        count = 0
        temp_dir = tempfile.gettempdir()
        cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)
        
        for filename in os.listdir(temp_dir):
            if filename.startswith('blood_donor_'):
                filepath = os.path.join(temp_dir, filename)
                if os.path.getmtime(filepath) < cutoff:
                    os.remove(filepath)
                    count += 1
        
        logger.info(f"Cleaned up {count} temporary files")
        return count
        
    except Exception as e:
        logger.error(f"Error cleaning up temp files: {str(e)}")
        return 0

def run_all_cleanup():
    """Run all cleanup tasks"""
    logger.info("Starting scheduled cleanup tasks")
    
    results = {
        'expired_requests': cleanup_expired_requests(),
        'old_exports': cleanup_old_exports(),
        'unverified_donations': cleanup_unverified_donations(),
        'inactive_users': cleanup_inactive_users(),
        'temp_files': cleanup_temp_files()
    }
    
    logger.info(f"Cleanup completed: {results}")
    return results