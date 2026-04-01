"""
Logging Middleware - Log requests and responses
"""

import time
from flask import request, g
from app.utils.logger import logger

class LoggingMiddleware:
    """Request/response logging middleware"""
    
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize middleware with app"""
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        app.teardown_request(self.teardown_request)
    
    def before_request(self):
        """Log before request"""
        g.start_time = time.time()
        
        # Log request
        log_data = {
            'method': request.method,
            'path': request.path,
            'ip': request.remote_addr,
            'user_agent': request.user_agent.string,
            'content_type': request.content_type,
            'content_length': request.content_length
        }
        
        # Add user info if authenticated
        from flask_login import current_user
        if current_user and current_user.is_authenticated:
            log_data['user_id'] = current_user.id
            log_data['user_role'] = current_user.role
        
        # Log based on path
        if request.path.startswith('/api/'):
            logger.debug(f"API Request: {log_data}")
        else:
            logger.info(f"Web Request: {log_data}")
    
    def after_request(self, response):
        """Log after request"""
        # Calculate duration
        duration = time.time() - g.get('start_time', time.time())
        
        # Log response
        log_data = {
            'method': request.method,
            'path': request.path,
            'status': response.status_code,
            'duration_ms': round(duration * 1000, 2)
        }
        
        # Add size for non-streaming responses
        if response.direct_passthrough:
            log_data['content_length'] = response.content_length
        
        # Log based on status
        if response.status_code >= 500:
            logger.error(f"Server Error: {log_data}")
        elif response.status_code >= 400:
            logger.warning(f"Client Error: {log_data}")
        else:
            if request.path.startswith('/api/'):
                logger.debug(f"API Response: {log_data}")
            else:
                logger.info(f"Web Response: {log_data}")
        
        # Add timing header
        response.headers['X-Response-Time'] = str(log_data['duration_ms'])
        
        return response
    
    def teardown_request(self, exception=None):
        """Log after request teardown"""
        if exception:
            logger.error(f"Request teardown error: {str(exception)}", exc_info=True)

class RequestLogger:
    """Decorator for logging specific requests"""
    
    @staticmethod
    def log_route(level='info'):
        """Decorator to log specific route"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                # Log before
                logger.log(
                    getattr(logging, level.upper()),
                    f"Entering {f.__name__} with args: {args}, kwargs: {kwargs}"
                )
                
                try:
                    result = f(*args, **kwargs)
                    
                    # Log after
                    logger.log(
                        getattr(logging, level.upper()),
                        f"Exiting {f.__name__}"
                    )
                    
                    return result
                    
                except Exception as e:
                    logger.error(f"Error in {f.__name__}: {str(e)}", exc_info=True)
                    raise
            
            return decorated_function
        return decorator
    
    @staticmethod
    def log_performance(f):
        """Decorator to log function performance"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start = time.time()
            
            result = f(*args, **kwargs)
            
            duration = time.time() - start
            logger.debug(f"{f.__name__} took {duration*1000:.2f}ms")
            
            return result
        
        return decorated_function

from functools import wraps
import logging