# """
# Authentication Blueprint - Login, Register, Logout
# """

# from flask import Blueprint, render_template, redirect, url_for, flash, request
# from flask_login import login_user, logout_user, current_user, login_required
# from app import db
# from app.models.user import User
# from app.models.donor import Donor
# from app.blueprints.auth.forms import LoginForm, RegistrationForm
# from datetime import datetime

# auth_bp = Blueprint('auth', __name__, template_folder='templates')

# @auth_bp.route('/login', methods=['GET', 'POST'])
# def login():
#     """User login route"""
#     if current_user.is_authenticated:
#         if current_user.is_admin():
#             return redirect(url_for('admin.dashboard'))
#         return redirect(url_for('donor.dashboard'))
    
#     form = LoginForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(email=form.email.data).first()
        
#         if user and user.check_password(form.password.data):
#             if not user.is_active:
#                 flash('Your account has been deactivated. Please contact admin.', 'danger')
#                 return redirect(url_for('auth.login'))
            
#             login_user(user, remember=form.remember.data)
#             user.update_last_login()
            
#             flash(f'Welcome back, {user.name}!', 'success')
            
#             next_page = request.args.get('next')
#             if next_page:
#                 return redirect(next_page)
            
#             if user.is_admin():
#                 return redirect(url_for('admin.dashboard'))
#             return redirect(url_for('donor.dashboard'))
#         else:
#             flash('Invalid email or password', 'danger')
    
#     return render_template('auth/login.html', form=form, title='Login')

# # @auth_bp.route('/register', methods=['GET', 'POST'])
# # def register():
# #     """User registration route"""
# #     if current_user.is_authenticated:
# #         return redirect(url_for('index'))
    
# #     form = RegistrationForm()
# #     if form.validate_on_submit():
# #         # Check if user exists
# #         if User.query.filter_by(email=form.email.data).first():
# #             flash('Email already registered', 'danger')
# #             return redirect(url_for('auth.register'))
        
# #         if User.query.filter_by(phone=form.phone.data).first():
# #             flash('Phone number already registered', 'danger')
# #             return redirect(url_for('auth.register'))
        
# #         # Create new user
# #         user = User(
# #             email=form.email.data,
# #             name=form.name.data,
# #             phone=form.phone.data,
# #             role='donor'
# #         )
# #         user.set_password(form.password.data)
        
# #         db.session.add(user)
# #         db.session.flush()  # Get user ID
        
# #         # Create donor profile
# #         donor = Donor(
# #             user_id=user.id,
# #             blood_type=form.blood_type.data,
# #             date_of_birth=form.date_of_birth.data,
# #             gender=form.gender.data,
# #             weight=form.weight.data,
# #             address=form.address.data,
# #             city=form.city.data,
# #             state=form.state.data,
# #             pincode=form.pincode.data,
# #             emergency_contact_name=form.emergency_contact_name.data,
# #             emergency_contact_phone=form.emergency_contact_phone.data,
# #             emergency_contact_relation=form.emergency_contact_relation.data
# #         )
        
# #         db.session.add(donor)
# #         db.session.commit()
        
# #         flash('Registration successful! Please login to continue.', 'success')
# #         return redirect(url_for('auth.login'))
    
# #     return render_template('auth/register.html', form=form, title='Register')

# @auth_bp.route('/register', methods=['GET', 'POST'])
# def register():
#     """User registration route"""
#     if current_user.is_authenticated:
#         return redirect(url_for('index'))
    
#     form = RegistrationForm()
#     if form.validate_on_submit():
#         # Check if user exists
#         if User.query.filter_by(email=form.email.data).first():
#             flash('Email already registered', 'danger')
#             return redirect(url_for('auth.register'))
        
#         if User.query.filter_by(phone=form.phone.data).first():
#             flash('Phone number already registered', 'danger')
#             return redirect(url_for('auth.register'))
        
#         # Create new user
#         user = User(
#             email=form.email.data,
#             name=form.name.data,
#             phone=form.phone.data,
#             role='donor'
#         )
#         user.set_password(form.password.data)
        
#         db.session.add(user)
#         db.session.flush()  # Get user ID
        
#         # Handle previous donations
#         last_donation_date = None
#         total_donations = 0
        
#         if request.form.get('has_previous_donations') == 'yes':
#             last_date = request.form.get('last_donation_date')
#             if last_date:
#                 last_donation_date = datetime.strptime(last_date, '%Y-%m-%d')
#             total_donations = int(request.form.get('total_previous_donations', 0))
        
#         # Create donor profile - unique ID will be auto-generated by model
#         donor = Donor(
#             user_id=user.id,
#             blood_type=form.blood_type.data,
#             date_of_birth=form.date_of_birth.data,
#             gender=form.gender.data,
#             weight=form.weight.data,
#             address=form.address.data,
#             city=form.city.data,
#             state=form.state.data,
#             pincode=form.pincode.data,
#             emergency_contact_name=form.emergency_contact_name.data,
#             emergency_contact_phone=form.emergency_contact_phone.data,
#             emergency_contact_relation=form.emergency_contact_relation.data,
#             last_donation_date=last_donation_date,
#             total_donations=total_donations,
#             nationality=request.form.get('nationality', 'Indian'),
#             has_disability=request.form.get('has_disability') == 'on',
#             disability=request.form.get('disability') if request.form.get('has_disability') == 'on' else None
#             # donor_unique_id will be auto-generated
#         )
        
#         db.session.add(donor)
#         db.session.commit()
        
#         # Check eligibility automatically
#         is_eligible, message, next_date = donor.check_eligibility()
#         donor.is_eligible = is_eligible
#         db.session.commit()
        
#         flash(f'Registration successful! Your Donor ID is: {donor.donor_unique_id}', 'success')
#         return redirect(url_for('auth.login'))
    
#     return render_template('auth/register.html', form=form, title='Register')

# @auth_bp.route('/logout')
# @login_required
# def logout():
#     """User logout route"""
#     logout_user()
#     flash('You have been logged out successfully.', 'info')
#     return redirect(url_for('index'))

# @auth_bp.route('/profile')
# @login_required
# def profile():
#     """View user profile"""
#     return render_template('auth/profile.html', title='My Profile')

# @auth_bp.route('/forgot-password', methods=['GET', 'POST'])
# def forgot_password():
#     """Forgot password route"""
#     flash('Password reset functionality coming soon. Please contact admin.', 'info')
#     return redirect(url_for('auth.login'))


"""
Authentication Blueprint - Login, Register, Logout
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, current_user, login_required
from app import db
from app.models.user import User
from app.models.donor import Donor
from app.blueprints.auth.forms import LoginForm, RegistrationForm
from app.services.upload_service import UploadService
from datetime import datetime
import os

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

# @auth_bp.route('/register', methods=['GET', 'POST'])
# def register():
#     """User registration route with photo upload"""
#     if current_user.is_authenticated:
#         return redirect(url_for('index'))
    
#     form = RegistrationForm()
    
#     if form.validate_on_submit():
#         # Check if user exists
#         if User.query.filter_by(email=form.email.data).first():
#             flash('Email already registered', 'danger')
#             return redirect(url_for('auth.register'))
        
#         if User.query.filter_by(phone=form.phone.data).first():
#             flash('Phone number already registered', 'danger')
#             return redirect(url_for('auth.register'))
        
#         # Create new user
#         user = User(
#             email=form.email.data,
#             name=form.name.data,
#             phone=form.phone.data,
#             role='donor'
#         )
#         user.set_password(form.password.data)
        
#         db.session.add(user)
#         db.session.flush()  # Get user ID
        
#         # Handle previous donations
#         last_donation_date = None
#         total_donations = 0
        
#         if request.form.get('has_previous_donations') == 'yes':
#             last_date = request.form.get('last_donation_date')
#             if last_date:
#                 try:
#                     last_donation_date = datetime.strptime(last_date, '%Y-%m-%d')
#                 except:
#                     pass
#             total_donations = int(request.form.get('total_previous_donations', 0))
        
#         # Create donor profile (unique ID will be auto-generated)
#         donor = Donor(
#             user_id=user.id,
#             blood_type=form.blood_type.data,
#             date_of_birth=form.date_of_birth.data,
#             gender=form.gender.data,
#             weight=form.weight.data,
#             address=form.address.data,
#             city=form.city.data,
#             state=form.state.data,
#             pincode=form.pincode.data,
#             emergency_contact_name=form.emergency_contact_name.data,
#             emergency_contact_phone=form.emergency_contact_phone.data,
#             emergency_contact_relation=form.emergency_contact_relation.data,
#             last_donation_date=last_donation_date,
#             total_donations=total_donations,
#             nationality=request.form.get('nationality', 'Indian'),
#             has_disability=request.form.get('has_disability') == 'on',
#             disability=request.form.get('disability') if request.form.get('has_disability') == 'on' else None
#         )
        
#         db.session.add(donor)
#         db.session.flush()  # Get donor ID and unique ID
        
#         # Handle profile photo upload
#         profile_photo = None
#         if form.profile_photo.data:
#             try:
#                 upload_service = UploadService()
#                 result = upload_service.save_uploaded_file(
#                     form.profile_photo.data, 
#                     donor.donor_unique_id
#                 )
#                 if result['success']:
#                     donor.profile_photo = result['filename']
#                     profile_photo = result['filename']
#                     flash('Profile photo uploaded successfully!', 'success')
#                 else:
#                     flash(f'Photo upload failed: {result["error"]}', 'warning')
#             except Exception as e:
#                 flash(f'Photo upload error: {str(e)}', 'warning')
        
#         db.session.commit()
        
#         # # Check eligibility automatically
#         # is_eligible, message, next_date = donor.check_eligibility()
#         # donor.is_eligible = is_eligible
#         # db.session.commit()

#         is_eligible, message, next_date = donor.check_eligibility()
#         donor.is_eligible = is_eligible
#         db.session.commit()

#         if next_date:
#            flash(f'Next eligible date: {next_date.strftime("%d %b, %Y")}', 'info')
        
#         flash(f'Registration successful! Your Donor ID is: {donor.donor_unique_id}', 'success')
#         return redirect(url_for('auth.login'))
    
#     return render_template('auth/register.html', form=form, title='Register')

# @auth_bp.route('/register', methods=['GET', 'POST'])
# def register():
#     """User registration route with photo upload"""
#     if current_user.is_authenticated:
#         return redirect(url_for('index'))
    
#     form = RegistrationForm()
    
#     if form.validate_on_submit():
#         # Check if user exists
#         if User.query.filter_by(email=form.email.data).first():
#             flash('Email already registered', 'danger')
#             return redirect(url_for('auth.register'))
        
#         if User.query.filter_by(phone=form.phone.data).first():
#             flash('Phone number already registered', 'danger')
#             return redirect(url_for('auth.register'))
        
#         # Create new user
#         user = User(
#             email=form.email.data,
#             name=form.name.data,
#             phone=form.phone.data,
#             role='donor'
#         )
#         user.set_password(form.password.data)
        
#         db.session.add(user)
#         db.session.flush()  # Get user ID
        
#         # Handle previous donations
#         last_donation_date = None
#         total_donations = 0
        
#         if request.form.get('has_previous_donations') == 'yes':
#             last_date = request.form.get('last_donation_date')
#             if last_date:
#                 try:
#                     last_donation_date = datetime.strptime(last_date, '%Y-%m-%d')
#                 except:
#                     pass
#             total_donations = int(request.form.get('total_previous_donations', 0))
        
#         # Create donor profile
#         donor = Donor(
#             user_id=user.id,
#             blood_type=form.blood_type.data,
#             date_of_birth=form.date_of_birth.data,
#             gender=form.gender.data,
#             weight=form.weight.data,
#             address=form.address.data,
#             city=form.city.data,
#             state=form.state.data,
#             pincode=form.pincode.data,
#             emergency_contact_name=form.emergency_contact_name.data,
#             emergency_contact_phone=form.emergency_contact_phone.data,
#             emergency_contact_relation=form.emergency_contact_relation.data,
#             last_donation_date=last_donation_date,
#             total_donations=total_donations,
#             nationality=request.form.get('nationality', 'Indian'),
#             has_disability=request.form.get('has_disability') == 'on',
#             disability=request.form.get('disability') if request.form.get('has_disability') == 'on' else None
#         )
        
#         db.session.add(donor)
#         db.session.flush()  # Get donor ID and unique ID
        
#         # Handle profile photo upload
#         if form.profile_photo.data:
#             try:
#                 upload_service = UploadService()
#                 result = upload_service.save_uploaded_file(
#                     form.profile_photo.data, 
#                     donor.donor_unique_id
#                 )
#                 if result['success']:
#                     donor.profile_photo = result['filename']
#                     flash('Profile photo uploaded successfully!', 'success')
#                 else:
#                     flash(f'Photo upload failed: {result["error"]}', 'warning')
#             except Exception as e:
#                 flash(f'Photo upload error: {str(e)}', 'warning')
        
#         # Final commit
#         db.session.commit()
        
#         # Check eligibility
#         is_eligible, message, next_date = donor.check_eligibility()
#         donor.is_eligible = is_eligible
#         db.session.commit()

#         if next_date:
#             flash(f'Next eligible date: {next_date.strftime("%d %b, %Y")}', 'info')
#         if not is_eligible:
#             flash(f'Eligibility note: {message}', 'info')
        
#         flash(f'Registration successful! Your Donor ID is: {donor.donor_unique_id}', 'success')
#         return redirect(url_for('auth.login'))
    
#     return render_template('auth/register.html', form=form, title='Register')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
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
        db.session.flush()
        
        # Handle previous donations
        last_donation_date = None
        total_donations = 0
        
        if request.form.get('has_previous_donations') == 'yes':
            last_date = request.form.get('last_donation_date')
            if last_date:
                last_donation_date = datetime.strptime(last_date, '%Y-%m-%d')
            total_donations = int(request.form.get('total_previous_donations', 0))
        
        # Create donor profile
        donor = Donor(
            donor_unique_id=Donor.generate_unique_id(),
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
            emergency_contact_relation=form.emergency_contact_relation.data,
            nationality=request.form.get('nationality', 'Indian'),
            has_disability=request.form.get('has_disability') == 'on',
            disability=request.form.get('disability') if request.form.get('has_disability') == 'on' else None,
            last_donation_date=last_donation_date,
            total_donations=total_donations
        )
        
        db.session.add(donor)
        db.session.commit()
        
        # Send welcome message
        from app.services.welcome_service import WelcomeService
        WelcomeService.send_welcome_message(user.id, user.name)
        
        # Check eligibility automatically
        is_eligible, message, next_date = donor.check_eligibility()
        donor.is_eligible = is_eligible
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
    return redirect(url_for('index'))

@auth_bp.route('/profile')
@login_required
def profile():
    """View user profile"""
    return render_template('auth/profile.html', title='My Profile')

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Forgot password route"""
    flash('Password reset functionality coming soon. Please contact admin.', 'info')
    return redirect(url_for('auth.login'))