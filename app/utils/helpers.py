"""
Helper utility functions
"""

import re
import hashlib
import random
import string
from datetime import datetime, timedelta
from flask import current_app

class Helpers:
    """Helper functions"""
    
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_phone(phone):
        """Validate phone number (10 digits)"""
        pattern = r'^\d{10}$'
        return re.match(pattern, phone) is not None
    
    @staticmethod
    def validate_pincode(pincode):
        """Validate pincode (6 digits)"""
        pattern = r'^\d{6}$'
        return re.match(pattern, pincode) is not None
    
    @staticmethod
    def sanitize_input(text):
        """Sanitize user input"""
        if not text:
            return text
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Escape special characters
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        text = text.replace('"', '&quot;')
        text = text.replace("'", '&#x27;')
        
        return text.strip()
    
    @staticmethod
    def generate_token(length=32):
        """Generate random token"""
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))
    
    @staticmethod
    def generate_otp(length=6):
        """Generate OTP"""
        return ''.join(random.choice(string.digits) for _ in range(length))
    
    @staticmethod
    def hash_string(text):
        """Create SHA-256 hash of string"""
        return hashlib.sha256(text.encode()).hexdigest()
    
    @staticmethod
    def format_date(date, format='%Y-%m-%d'):
        """Format date"""
        if not date:
            return ''
        if isinstance(date, str):
            date = datetime.strptime(date, '%Y-%m-%d')
        return date.strftime(format)
    
    @staticmethod
    def format_datetime(dt, format='%Y-%m-%d %H:%M:%S'):
        """Format datetime"""
        if not dt:
            return ''
        if isinstance(dt, str):
            dt = datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
        return dt.strftime(format)
    
    @staticmethod
    def time_ago(date):
        """Get human readable time ago"""
        if not date:
            return ''
        
        now = datetime.utcnow()
        diff = now - date
        
        if diff.days > 365:
            years = diff.days // 365
            return f"{years} year{'s' if years > 1 else ''} ago"
        elif diff.days > 30:
            months = diff.days // 30
            return f"{months} month{'s' if months > 1 else ''} ago"
        elif diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "just now"
    
    @staticmethod
    def truncate(text, length=100):
        """Truncate text to specified length"""
        if len(text) <= length:
            return text
        return text[:length] + '...'
    
    @staticmethod
    def slugify(text):
        """Convert text to URL slug"""
        # Convert to lowercase
        text = text.lower()
        
        # Replace spaces with hyphens
        text = re.sub(r'\s+', '-', text)
        
        # Remove special characters
        text = re.sub(r'[^a-z0-9-]', '', text)
        
        # Remove multiple hyphens
        text = re.sub(r'-+', '-', text)
        
        return text.strip('-')
    
    @staticmethod
    def parse_bool(value):
        """Parse boolean from various formats"""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ('true', 'yes', '1', 'y')
        if isinstance(value, (int, float)):
            return bool(value)
        return False
    
    @staticmethod
    def get_file_extension(filename):
        """Get file extension"""
        if '.' in filename:
            return filename.rsplit('.', 1)[1].lower()
        return ''
    
    @staticmethod
    def is_allowed_file(filename, allowed_extensions):
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in allowed_extensions
    
    @staticmethod
    def format_currency(amount):
        """Format currency"""
        return f"₹{amount:,.2f}"
    
    @staticmethod
    def format_percentage(value):
        """Format percentage"""
        return f"{value:.1f}%"
    
    @staticmethod
    def group_by(items, key_func):
        """Group items by key"""
        result = {}
        for item in items:
            key = key_func(item)
            if key not in result:
                result[key] = []
            result[key].append(item)
        return result
    
    @staticmethod
    def chunks(lst, n):
        """Split list into chunks"""
        for i in range(0, len(lst), n):
            yield lst[i:i + n]