"""
Auth API - Authentication endpoints for mobile apps
"""

from flask import Blueprint, request, jsonify
from app import db
from app.models.user import User
from flask_login import login_user, logout_user
from datetime import datetime
import jwt
import os

auth_api_bp = Blueprint('auth_api', __name__, url_prefix='/api/auth')

@auth_api_bp.route('/login', methods=['POST'])
def api_login():
    """API login endpoint"""
    try:
        data = request.get_json()
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                return jsonify({'error': 'Account deactivated'}), 403
            
            user.update_last_login()
            
            # Generate token (JWT)
            token = jwt.encode({
                'user_id': user.id,
                'email': user.email,
                'role': user.role,
                'exp': datetime.utcnow() + timedelta(days=1)
            }, os.environ.get('SECRET_KEY', 'secret'), algorithm='HS256')
            
            return jsonify({
                'status': 'success',
                'token': token,
                'user': {
                    'id': user.id,
                    'name': user.name,
                    'email': user.email,
                    'role': user.role
                }
            })
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_api_bp.route('/register', methods=['POST'])
def api_register():
    """API registration endpoint"""
    try:
        data = request.get_json()
        
        # Check if user exists
        if User.query.filter_by(email=data.get('email')).first():
            return jsonify({'error': 'Email already registered'}), 400
        
        if User.query.filter_by(phone=data.get('phone')).first():
            return jsonify({'error': 'Phone already registered'}), 400
        
        # Create user
        user = User(
            email=data.get('email'),
            name=data.get('name'),
            phone=data.get('phone'),
            role='donor'
        )
        user.set_password(data.get('password'))
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Registration successful',
            'user_id': user.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_api_bp.route('/logout', methods=['POST'])
def api_logout():
    """API logout endpoint"""
    # JWT tokens are stateless, so we just return success
    return jsonify({'status': 'success', 'message': 'Logged out'})

from datetime import timedelta