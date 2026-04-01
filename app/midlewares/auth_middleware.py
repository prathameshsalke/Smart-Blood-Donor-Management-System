"""
Authentication Middleware - Handle authentication checks
"""

from functools import wraps
from flask import request, jsonify, redirect, url_for, flash
from flask_login import current_user
from app.utils.logger import logger

class AuthMiddleware:
    """Authentication middleware"""
    
    @staticmethod
    def login_required(f):
        """Require user to be logged in"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                # Check if it's an API request
                if request.path.startswith('/api/'):
                    return jsonify({
                        'status': 'error',
                        'message': 'Authentication required'
                    }), 401
                
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login', next=request.url))
            
            return f(*args, **kwargs)
        return decorated_function
    
    @staticmethod
    def admin_required(f):
        """Require admin privileges"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                if request.path.startswith('/api/'):
                    return jsonify({
                        'status': 'error',
                        'message': 'Authentication required'
                    }), 401
                
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login', next=request.url))
            
            if not current_user.is_admin():
                logger.warning(f"Unauthorized admin access attempt by user {current_user.id}")
                
                if request.path.startswith('/api/'):
                    return jsonify({
                        'status': 'error',
                        'message': 'Admin privileges required'
                    }), 403
                
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for('main.index'))
            
            return f(*args, **kwargs)
        return decorated_function
    
    @staticmethod
    def donor_required(f):
        """Require donor privileges"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                if request.path.startswith('/api/'):
                    return jsonify({
                        'status': 'error',
                        'message': 'Authentication required'
                    }), 401
                
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login', next=request.url))
            
            if not current_user.is_donor():
                if request.path.startswith('/api/'):
                    return jsonify({
                        'status': 'error',
                        'message': 'Donor privileges required'
                    }), 403
                
                flash('This page is only for registered donors.', 'danger')
                return redirect(url_for('main.index'))
            
            return f(*args, **kwargs)
        return decorated_function
    
    @staticmethod
    def api_key_required(f):
        """Require valid API key"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            api_key = request.headers.get('X-API-Key')
            
            if not api_key:
                return jsonify({
                    'status': 'error',
                    'message': 'API key required'
                }), 401
            
            # Validate API key (implement your logic)
            from app.models.api_key import APIKey
            key = APIKey.query.filter_by(key=api_key, is_active=True).first()
            
            if not key:
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid API key'
                }), 401
            
            # Add key info to request
            request.api_key = key
            
            return f(*args, **kwargs)
        return decorated_function
    
    @staticmethod
    def token_required(f):
        """Require valid JWT token"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            
            if not token:
                return jsonify({
                    'status': 'error',
                    'message': 'Token required'
                }), 401
            
            try:
                import jwt
                from flask import current_app
                
                # Decode token
                payload = jwt.decode(
                    token,
                    current_app.config['SECRET_KEY'],
                    algorithms=['HS256']
                )
                
                # Get user
                from app.models.user import User
                user = User.query.get(payload['user_id'])
                
                if not user or not user.is_active:
                    return jsonify({
                        'status': 'error',
                        'message': 'Invalid token'
                    }), 401
                
                # Add user to request
                request.current_user = user
                
            except jwt.ExpiredSignatureError:
                return jsonify({
                    'status': 'error',
                    'message': 'Token has expired'
                }), 401
            except jwt.InvalidTokenError:
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid token'
                }), 401
            
            return f(*args, **kwargs)
        return decorated_function
    
    @staticmethod
    def check_active(f):
        """Check if user account is active"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.is_authenticated and not current_user.is_active:
                if request.path.startswith('/api/'):
                    return jsonify({
                        'status': 'error',
                        'message': 'Account deactivated'
                    }), 403
                
                flash('Your account has been deactivated. Please contact admin.', 'danger')
                return redirect(url_for('auth.logout'))
            
            return f(*args, **kwargs)
        return decorated_function