"""
Authentication Blueprint - Login, Register, Logout
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app import db
from app.models.user import User
from app.models.donor import Donor
from app.blueprints.auth.forms import LoginForm, RegistrationForm
from datetime import datetime

auth_bp = Blueprint('auth', __name__, template_folder='templates')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login route"""
    if current_user.is_authenticated:
        if current_user.is_admin():
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('donor.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact admin.', 'danger')
                return redirect(url_for('auth.login'))
            
            login_user(user, remember=form.remember.data)
            user.update_last_login()
            
            flash(f'Welcome back, {user.name}!', 'success')
            
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            
            if user.is_admin():
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('donor.dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('auth/login.html', form=form, title='Login')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))  # Fixed: changed from main.index to index
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if user exists
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(phone=form.phone.data).first():
            flash('Phone number already registered', 'danger')
            return redirect(url_for('auth.register'))
        
        # Create new user
        user = User(
            email=form.email.data,
            name=form.name.data,
            phone=form.phone.data,
            role='donor'
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.flush()  # Get user ID
        
        # Create donor profile
        donor = Donor(
            user_id=user.id,
            blood_type=form.blood_type.data,
            date_of_birth=form.date_of_birth.data,
            gender=form.gender.data,
            weight=form.weight.data,
            address=form.address.data,
            city=form.city.data,
            state=form.state.data,
            pincode=form.pincode.data,
            emergency_contact_name=form.emergency_contact_name.data,
            emergency_contact_phone=form.emergency_contact_phone.data,
            emergency_contact_relation=form.emergency_contact_relation.data
        )
        
        db.session.add(donor)
        db.session.commit()
        
        flash('Registration successful! Please login to continue.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form, title='Register')

@auth_bp.route('/logout')
@login_required
def logout():
    """User logout route"""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))  # Fixed: changed from main.index to index

@auth_bp.route('/profile')
@login_required
def profile():
    """View user profile"""
    return render_template('auth/profile.html', title='My Profile')

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Forgot password route"""
    # For now, just redirect to login with a message
    # You can implement actual password reset functionality later
    flash('Password reset functionality coming soon. Please contact admin.', 'info')
    return redirect(url_for('auth.login'))
    # When you implement the template, uncomment this:
    # return render_template('auth/forgot_password.html', title='Forgot Password')