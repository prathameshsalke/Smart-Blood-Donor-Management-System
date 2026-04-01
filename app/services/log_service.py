"""
Log Service - Handle system logging
"""

from app import db
from app.models.admin_log import AdminLog
from app.utils.logger import logger
from flask import request
from datetime import datetime

class LogService:
    """Service for logging system activities"""
    
    @staticmethod
    def log_admin_action(admin_id, admin_email, action, entity_type, entity_id=None, description=None, old_values=None, new_values=None):
        """Log admin action"""
        try:
            log = AdminLog(
                admin_id=admin_id,
                admin_email=admin_email,
                action=action,
                entity_type=entity_type,
                entity_id=str(entity_id) if entity_id else None,
                description=description,
                ip_address=request.remote_addr if request else None,
                old_values=old_values,
                new_values=new_values
            )
            
            db.session.add(log)
            db.session.commit()
            
            logger.info(f"Admin action logged: {action} on {entity_type} by {admin_email}")
            return log
            
        except Exception as e:
            logger.error(f"Error logging admin action: {str(e)}")
            db.session.rollback()
            return None
    
    @staticmethod
    def log_user_action(user_id, action, details=None):
        """Log user action"""
        try:
            log_data = {
                'timestamp': datetime.utcnow().isoformat(),
                'user_id': user_id,
                'action': action,
                'details': details or {},
                'ip': request.remote_addr if request else None,
                'user_agent': request.user_agent.string if request else None
            }
            
            logger.info(f"User action: {action} by user {user_id}")
            return log_data
            
        except Exception as e:
            logger.error(f"Error logging user action: {str(e)}")
            return None
    
    @staticmethod
    def log_api_call(endpoint, user_id=None, params=None, response_code=None):
        """Log API call"""
        try:
            log_data = {
                'timestamp': datetime.utcnow().isoformat(),
                'endpoint': endpoint,
                'user_id': user_id,
                'params': params or {},
                'response_code': response_code,
                'ip': request.remote_addr if request else None,
                'method': request.method if request else None
            }
            
            logger.debug(f"API call: {endpoint} by user {user_id}")
            return log_data
            
        except Exception as e:
            logger.error(f"Error logging API call: {str(e)}")
            return None
    
    @staticmethod
    def log_error(error, context=None):
        """Log error"""
        try:
            log_data = {
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(error),
                'error_type': type(error).__name__,
                'context': context or {},
                'path': request.path if request else None,
                'method': request.method if request else None
            }
            
            logger.error(f"Error: {str(error)}", exc_info=True)
            return log_data
            
        except Exception as e:
            logger.error(f"Error in log_error: {str(e)}")
            return None
    
    @staticmethod
    def get_admin_logs(limit=100, admin_id=None, action=None, entity_type=None):
        """Get admin logs with filters"""
        try:
            query = AdminLog.query.order_by(AdminLog.created_at.desc())
            
            if admin_id:
                query = query.filter_by(admin_id=admin_id)
            if action:
                query = query.filter_by(action=action)
            if entity_type:
                query = query.filter_by(entity_type=entity_type)
            
            logs = query.limit(limit).all()
            return logs
            
        except Exception as e:
            logger.error(f"Error getting admin logs: {str(e)}")
            return []
    
    @staticmethod
    def get_logs_by_date(start_date, end_date, log_type='admin'):
        """Get logs within date range"""
        try:
            if log_type == 'admin':
                logs = AdminLog.query.filter(
                    AdminLog.created_at.between(start_date, end_date)
                ).order_by(AdminLog.created_at.desc()).all()
            else:
                # For file logs, we'd need to parse log files
                logs = []
            
            return logs
            
        except Exception as e:
            logger.error(f"Error getting logs by date: {str(e)}")
            return []
    
    @staticmethod
    def cleanup_old_logs(days=30):
        """Delete logs older than specified days"""
        try:
            from datetime import timedelta
            cutoff = datetime.utcnow() - timedelta(days=days)
            
            # Delete admin logs
            old_logs = AdminLog.query.filter(AdminLog.created_at < cutoff).all()
            count = len(old_logs)
            
            for log in old_logs:
                db.session.delete(log)
            
            db.session.commit()
            
            logger.info(f"Cleaned up {count} old logs")
            return count
            
        except Exception as e:
            logger.error(f"Error cleaning up logs: {str(e)}")
            db.session.rollback()
            return 0