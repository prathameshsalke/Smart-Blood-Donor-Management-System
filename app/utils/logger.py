"""
Logging utility
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime
from flask import request, session

class Logger:
    """Application logger"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize logger"""
        # Create logs directory
        log_dir = 'logs'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Configure logger
        self.logger = logging.getLogger('BloodDonorSystem')
        self.logger.setLevel(logging.INFO)
        
        # File handler
        log_file = os.path.join(log_dir, f'app_{datetime.now().strftime("%Y%m%d")}.log')
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10485760,  # 10MB
            backupCount=10
        )
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def info(self, message, *args, **kwargs):
        """Log info message"""
        self.logger.info(message, *args, **kwargs)
    
    def warning(self, message, *args, **kwargs):
        """Log warning message"""
        self.logger.warning(message, *args, **kwargs)
    
    def error(self, message, *args, **kwargs):
        """Log error message"""
        self.logger.error(message, *args, **kwargs)
    
    def debug(self, message, *args, **kwargs):
        """Log debug message"""
        self.logger.debug(message, *args, **kwargs)
    
    def critical(self, message, *args, **kwargs):
        """Log critical message"""
        self.logger.critical(message, *args, **kwargs)
    
    def log_request(self, response=None):
        """Log HTTP request"""
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'method': request.method,
            'path': request.path,
            'ip': request.remote_addr,
            'user_agent': request.user_agent.string,
            'user_id': session.get('user_id'),
            'status_code': response.status_code if response else None
        }
        
        self.info(f"Request: {log_data}")
    
    def log_error(self, error, context=None):
        """Log error with context"""
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(error),
            'error_type': type(error).__name__,
            'context': context or {},
            'path': request.path if request else None,
            'method': request.method if request else None,
            'user_id': session.get('user_id') if session else None
        }
        
        self.error(f"Error: {log_data}")
    
    def log_admin_action(self, admin_id, action, entity, details=None):
        """Log admin action"""
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'admin_id': admin_id,
            'action': action,
            'entity': entity,
            'details': details or {},
            'ip': request.remote_addr if request else None
        }
        
        self.info(f"Admin Action: {log_data}")
    
    def log_api_call(self, endpoint, params=None, user_id=None):
        """Log API call"""
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'endpoint': endpoint,
            'params': params or {},
            'user_id': user_id,
            'ip': request.remote_addr if request else None
        }
        
        self.debug(f"API Call: {log_data}")

# Create singleton instance
logger = Logger()

# ===== ADD THESE FUNCTIONS =====
def log_admin_activity(admin_id, action, entity, details=None):
    """Convenience function to log admin activity"""
    logger.log_admin_action(admin_id, action, entity, details)

def log_user_activity(user_id, action, details=None):
    """Log user activity"""
    log_data = {
        'timestamp': datetime.utcnow().isoformat(),
        'user_id': user_id,
        'action': action,
        'details': details or {}
    }
    logger.info(f"User Activity: {log_data}")

def log_system_event(event, details=None):
    """Log system event"""
    log_data = {
        'timestamp': datetime.utcnow().isoformat(),
        'event': event,
        'details': details or {}
    }
    logger.info(f"System Event: {log_data}")