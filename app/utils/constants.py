"""
Constants - Application-wide constant values
"""

from datetime import timedelta

# Blood Types
BLOOD_TYPES = [
    ('A+', 'A+'),
    ('A-', 'A-'),
    ('B+', 'B+'),
    ('B-', 'B-'),
    ('AB+', 'AB+'),
    ('AB-', 'AB-'),
    ('O+', 'O+'),
    ('O-', 'O-')
]

BLOOD_TYPE_COMPATIBILITY = {
    'A+': {
        'can_donate_to': ['A+', 'AB+'],
        'can_receive_from': ['A+', 'A-', 'O+', 'O-']
    },
    'A-': {
        'can_donate_to': ['A+', 'A-', 'AB+', 'AB-'],
        'can_receive_from': ['A-', 'O-']
    },
    'B+': {
        'can_donate_to': ['B+', 'AB+'],
        'can_receive_from': ['B+', 'B-', 'O+', 'O-']
    },
    'B-': {
        'can_donate_to': ['B+', 'B-', 'AB+', 'AB-'],
        'can_receive_from': ['B-', 'O-']
    },
    'AB+': {
        'can_donate_to': ['AB+'],
        'can_receive_from': ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    },
    'AB-': {
        'can_donate_to': ['AB+', 'AB-'],
        'can_receive_from': ['A-', 'B-', 'AB-', 'O-']
    },
    'O+': {
        'can_donate_to': ['O+', 'A+', 'B+', 'AB+'],
        'can_receive_from': ['O+', 'O-']
    },
    'O-': {
        'can_donate_to': ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'],
        'can_receive_from': ['O-']
    }
}

# User Roles
USER_ROLES = [
    ('donor', 'Donor'),
    ('admin', 'Administrator'),
    ('hospital', 'Hospital Staff'),
    ('staff', 'Staff')
]

# Gender Options
GENDERS = [
    ('male', 'Male'),
    ('female', 'Female'),
    ('other', 'Other')
]

# Urgency Levels
URGENCY_LEVELS = [
    ('low', 'Low'),
    ('medium', 'Medium'),
    ('high', 'High'),
    ('emergency', 'Emergency')
]

# Request Status
REQUEST_STATUS = [
    ('pending', 'Pending'),
    ('fulfilled', 'Fulfilled'),
    ('cancelled', 'Cancelled'),
    ('expired', 'Expired')
]

# Donation Eligibility Rules
ELIGIBILITY_RULES = {
    'min_age': 18,
    'max_age': 65,
    'min_weight_kg': 45,
    'donation_interval_days': 90,
    'max_donations_per_year': 4,
    'hemoglobin_min': 12.5,  # g/dL
    'hemoglobin_max': 18.0,
    'bp_systolic_min': 90,
    'bp_systolic_max': 180,
    'bp_diastolic_min': 60,
    'bp_diastolic_max': 100
}

# Search Radius (km)
DEFAULT_SEARCH_RADIUS = 10
EMERGENCY_SEARCH_RADIUS = 10
HOSPITAL_SEARCH_RADIUS = 20
MAX_SEARCH_RADIUS = 100

# Time Constants
DONATION_COOLDOWN = timedelta(days=90)
REQUEST_EXPIRY_EMERGENCY = timedelta(hours=48)
REQUEST_EXPIRY_NORMAL = timedelta(days=7)
SESSION_TIMEOUT = timedelta(days=7)
REMEMBER_COOKIE_DURATION = timedelta(days=30)

# Pagination
ITEMS_PER_PAGE = 20
MAX_PAGE_SIZE = 100

# File Upload
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
UPLOAD_FOLDERS = {
    'profile': 'uploads/profiles',
    'certificate': 'uploads/certificates',
    'temp': 'uploads/temp'
}

# Certificate Settings
CERTIFICATE_EXPIRY_DAYS = 365
QR_CODE_SIZE = 10
CERTIFICATE_TITLE = "Blood Donation Certificate"

# Notification Types
NOTIFICATION_TYPES = {
    'emergency_alert': '🚨 Emergency Blood Request',
    'request_update': '📋 Request Update',
    'donation_confirmation': '✅ Donation Confirmed',
    'eligibility_reminder': '⏰ Eligibility Reminder',
    'welcome': '👋 Welcome',
    'thank_you': '🙏 Thank You',
    'admin_alert': '⚠️ Admin Alert'
}

# API Rate Limits
RATE_LIMITS = {
    'default': '100/hour',
    'emergency': '10/minute',
    'search': '30/minute',
    'auth': '5/minute'
}

# Cache Keys
CACHE_KEYS = {
    'donor_stats': 'donor_stats',
    'request_stats': 'request_stats',
    'nearby_donors': 'nearby_donors:{lat}:{lon}:{radius}',
    'blood_type_distribution': 'blood_type_distribution',
    'hospital_list': 'hospital_list'
}

# Log Categories
LOG_CATEGORIES = {
    'auth': 'Authentication',
    'donor': 'Donor Management',
    'request': 'Blood Request',
    'admin': 'Admin Action',
    'api': 'API Call',
    'system': 'System',
    'error': 'Error'
}

# Error Messages
ERROR_MESSAGES = {
    'auth_required': 'Please log in to access this page.',
    'admin_required': 'Admin privileges required.',
    'donor_required': 'Donor registration required.',
    'invalid_credentials': 'Invalid email or password.',
    'account_inactive': 'Your account has been deactivated.',
    'not_found': 'Resource not found.',
    'permission_denied': 'You do not have permission to perform this action.',
    'validation_error': 'Please check your input and try again.',
    'server_error': 'An internal server error occurred.'
}

# Success Messages
SUCCESS_MESSAGES = {
    'login': 'Welcome back, {name}!',
    'logout': 'You have been logged out successfully.',
    'register': 'Registration successful! Please log in.',
    'profile_updated': 'Profile updated successfully.',
    'donation_recorded': 'Thank you for donating blood!',
    'request_created': 'Blood request created successfully.',
    'request_fulfilled': 'Request marked as fulfilled.',
    'certificate_generated': 'Certificate generated successfully.'
}

# Map Settings
MAP_DEFAULT_CENTER = {'lat': 20.5937, 'lng': 78.9629}  # India center
MAP_DEFAULT_ZOOM = 5
MAP_TILE_LAYER = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
MAP_ATTRIBUTION = '© OpenStreetMap contributors'

# Chart Colors
CHART_COLORS = {
    'primary': '#dc3545',
    'secondary': '#6c757d',
    'success': '#28a745',
    'info': '#17a2b8',
    'warning': '#ffc107',
    'danger': '#dc3545',
    'light': '#f8f9fa',
    'dark': '#343a40'
}

# Blood Type Colors (for charts)
BLOOD_TYPE_COLORS = {
    'A+': '#dc3545',
    'A-': '#dc354580',
    'B+': '#28a745',
    'B-': '#28a74580',
    'AB+': '#17a2b8',
    'AB-': '#17a2b880',
    'O+': '#ffc107',
    'O-': '#ffc10780'
}