"""
Role Middleware - Handle role-based access control
"""

from functools import wraps
from flask import request, jsonify, abort
from flask_login import current_user
from app.utils.logger import logger

class RoleMiddleware:
    """Role-based access control middleware"""
    
    @staticmethod
    def role_required(*roles):
        """Require specific role(s)"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if not current_user.is_authenticated:
                    if request.path.startswith('/api/'):
                        return jsonify({
                            'status': 'error',
                            'message': 'Authentication required'
                        }), 401
                    abort(401)
                
                if current_user.role not in roles:
                    logger.warning(
                        f"Access denied: User {current_user.id} with role "
                        f"{current_user.role} tried to access {request.path}"
                    )
                    
                    if request.path.startswith('/api/'):
                        return jsonify({
                            'status': 'error',
                            'message': 'Insufficient permissions'
                        }), 403
                    abort(403)
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    @staticmethod
    def permission_required(permission):
        """Require specific permission"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if not current_user.is_authenticated:
                    if request.path.startswith('/api/'):
                        return jsonify({
                            'status': 'error',
                            'message': 'Authentication required'
                        }), 401
                    abort(401)
                
                # Check permission (implement your permission logic)
                if not current_user.has_permission(permission):
                    logger.warning(
                        f"Permission denied: User {current_user.id} "
                        f"tried to access {permission}"
                    )
                    
                    if request.path.startswith('/api/'):
                        return jsonify({
                            'status': 'error',
                            'message': 'Permission denied'
                        }), 403
                    abort(403)
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    @staticmethod
    def resource_owner_or_admin(resource_getter):
        """Check if user owns the resource or is admin"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if not current_user.is_authenticated:
                    if request.path.startswith('/api/'):
                        return jsonify({
                            'status': 'error',
                            'message': 'Authentication required'
                        }), 401
                    abort(401)
                
                # Get resource
                resource = resource_getter(*args, **kwargs)
                
                # Check ownership
                if not resource or (
                    resource.user_id != current_user.id and 
                    not current_user.is_admin()
                ):
                    logger.warning(
                        f"Unauthorized resource access: User {current_user.id} "
                        f"tried to access resource {resource.id if resource else 'unknown'}"
                    )
                    
                    if request.path.startswith('/api/'):
                        return jsonify({
                            'status': 'error',
                            'message': 'Access denied'
                        }), 403
                    abort(403)
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    @staticmethod
    def self_only(f):
        """Allow access only to own profile"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                if request.path.startswith('/api/'):
                    return jsonify({
                        'status': 'error',
                        'message': 'Authentication required'
                    }), 401
                abort(401)
            
            # Get user_id from kwargs
            user_id = kwargs.get('user_id')
            
            if user_id and int(user_id) != current_user.id and not current_user.is_admin():
                if request.path.startswith('/api/'):
                    return jsonify({
                        'status': 'error',
                        'message': 'You can only access your own profile'
                    }), 403
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function

# Role-based decorators
admin_required = RoleMiddleware.role_required('admin')
donor_required = RoleMiddleware.role_required('donor')
staff_required = RoleMiddleware.role_required('admin', 'staff')