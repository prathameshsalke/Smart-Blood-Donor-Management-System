# """
# Authentication Forms
# """

# from flask_wtf import FlaskForm
# from wtforms import StringField, PasswordField, BooleanField, SelectField, DateField, FloatField
# from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
# from datetime import date

# class LoginForm(FlaskForm):
#     """User login form"""
#     email = StringField('Email', validators=[DataRequired(), Email(), Length(1, 120)])
#     password = PasswordField('Password', validators=[DataRequired()])
#     remember = BooleanField('Remember Me')

# class RegistrationForm(FlaskForm):
#     """User registration form"""
#     # User account fields
#     name = StringField('Full Name', validators=[DataRequired(), Length(2, 100)])
#     email = StringField('Email', validators=[DataRequired(), Email(), Length(1, 120)])
#     phone = StringField('Phone Number', validators=[DataRequired(), Length(10, 20)])
#     password = PasswordField('Password', validators=[
#         DataRequired(),
#         Length(min=6, message='Password must be at least 6 characters')
#     ])
#     confirm_password = PasswordField('Confirm Password', validators=[
#         DataRequired(),
#         EqualTo('password', message='Passwords must match')
#     ])
    
#     # Donor profile fields
#     blood_type = SelectField('Blood Group', validators=[DataRequired()], choices=[
#         ('', 'Select Blood Group'),
#         ('A+', 'A+'), ('A-', 'A-'),
#         ('B+', 'B+'), ('B-', 'B-'),
#         ('AB+', 'AB+'), ('AB-', 'AB-'),
#         ('O+', 'O+'), ('O-', 'O-')
#     ])
    
#     date_of_birth = DateField('Date of Birth', validators=[DataRequired()], format='%Y-%m-%d')
    
#     gender = SelectField('Gender', validators=[DataRequired()], choices=[
#         ('', 'Select Gender'),
#         ('male', 'Male'),
#         ('female', 'Female'),
#         ('other', 'Other')
#     ])
    
#     weight = FloatField('Weight (kg)', validators=[DataRequired()])
    
#     address = StringField('Address', validators=[DataRequired(), Length(5, 200)])
#     city = StringField('City', validators=[DataRequired(), Length(2, 50)])
#     state = StringField('State', validators=[DataRequired(), Length(2, 50)])
#     pincode = StringField('Pincode', validators=[DataRequired(), Length(6, 10)])
    
#     # Emergency contact
#     emergency_contact_name = StringField('Emergency Contact Name', validators=[DataRequired(), Length(2, 100)])
#     emergency_contact_phone = StringField('Emergency Contact Phone', validators=[DataRequired(), Length(10, 20)])
#     emergency_contact_relation = StringField('Relationship', validators=[DataRequired(), Length(2, 50)])
    
#     def validate_date_of_birth(self, field):
#         """Validate age (must be 18-65)"""
#         today = date.today()
#         age = today.year - field.data.year
#         if today.month < field.data.month or (today.month == field.data.month and today.day < field.data.day):
#             age -= 1
        
#         if age < 18:
#             raise ValidationError('You must be at least 18 years old to register')
#         if age > 65:
#             raise ValidationError('Age must be less than 65 years')
    
#     def validate_weight(self, field):
#         """Validate weight (minimum 45 kg)"""
#         if field.data < 45:
#             raise ValidationError('Weight must be at least 45 kg for blood donation')


"""
Authentication Forms
"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SelectField, DateField, FloatField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from datetime import date

class LoginForm(FlaskForm):
    """User login form"""
    email = StringField('Email', validators=[DataRequired(), Email(), Length(1, 120)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')

class RegistrationForm(FlaskForm):
    """User registration form with photo upload"""
    # User account fields
    name = StringField('Full Name', validators=[DataRequired(), Length(2, 100)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(1, 120)])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(10, 20)])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6, message='Password must be at least 6 characters')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    
    # Profile Photo
    profile_photo = FileField('Profile Photo', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])
    
    # Donor profile fields
    blood_type = SelectField('Blood Group', validators=[DataRequired()], choices=[
        ('', 'Select Blood Group'),
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-')
    ])
    
    date_of_birth = DateField('Date of Birth', validators=[DataRequired()], format='%Y-%m-%d')
    
    gender = SelectField('Gender', validators=[DataRequired()], choices=[
        ('', 'Select Gender'),
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ])
    
    weight = FloatField('Weight (kg)', validators=[DataRequired()])
    
    address = StringField('Address', validators=[DataRequired(), Length(5, 200)])
    city = StringField('City', validators=[DataRequired(), Length(2, 50)])
    state = StringField('State', validators=[DataRequired(), Length(2, 50)])
    pincode = StringField('Pincode', validators=[DataRequired(), Length(6, 10)])
    
    # Emergency contact
    emergency_contact_name = StringField('Emergency Contact Name', validators=[DataRequired(), Length(2, 100)])
    emergency_contact_phone = StringField('Emergency Contact Phone', validators=[DataRequired(), Length(10, 20)])
    emergency_contact_relation = StringField('Relationship', validators=[DataRequired(), Length(2, 50)])
    
    # Nationality and Disability
    nationality = SelectField('Nationality', validators=[DataRequired()], choices=[
        ('Indian', 'Indian'),
        ('Other', 'Other')
    ], default='Indian')
    
    has_disability = BooleanField('I have a disability')
    
    disability = StringField('Please describe your disability', validators=[Length(0, 200)])
    
    # Previous Donation History
    has_previous_donations = SelectField('Have you donated blood before?', choices=[
        ('no', 'No, I\'m a first-time donor'),
        ('yes', 'Yes, I have donated before')
    ], default='no')
    
    last_donation_date = DateField('Last Donation Date', format='%Y-%m-%d', validators=[])
    
    total_previous_donations = StringField('Total Previous Donations', default='0')
    
    last_donation_location = StringField('Last Donation Location', validators=[Length(0, 100)])
    
    def validate_date_of_birth(self, field):
        """Validate age (must be 18-65)"""
        today = date.today()
        age = today.year - field.data.year
        if today.month < field.data.month or (today.month == field.data.month and today.day < field.data.day):
            age -= 1
        
        if age < 18:
            raise ValidationError('You must be at least 18 years old to register')
        if age > 65:
            raise ValidationError('Age must be less than 65 years')
    
    def validate_weight(self, field):
        """Validate weight (minimum 45 kg)"""
        if field.data < 45:
            raise ValidationError('Weight must be at least 45 kg for blood donation')