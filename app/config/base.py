"""
Base configuration - Common settings for all environments
"""

import os
from datetime import timedelta

class Config:
    """Base configuration class"""
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    
    # Database
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
    }
    
    # Application
    APP_NAME = os.environ.get('APP_NAME', 'Smart Blood Donor System')
    APP_URL = os.environ.get('APP_URL', 'http://localhost:5000')
    
    # File Upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'app/static/uploads')
    CERTIFICATE_FOLDER = os.path.join(os.getcwd(), 'app/static/certificates')
    
    # Mail Settings
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@blooddonor.com')
    
    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    REMEMBER_COOKIE_DURATION = timedelta(days=30)
    
    # Pagination
    ITEMS_PER_PAGE = 20
    
    # Geo settings
    DEFAULT_SEARCH_RADIUS = 10  # km
    EMERGENCY_SEARCH_RADIUS = 10  # km
    HOSPITAL_SEARCH_RADIUS = 20  # km
    
    # ML Model paths
    ML_MODELS_PATH = os.path.join(os.getcwd(), 'ml_models')
    DONOR_MODEL_PATH = os.path.join(ML_MODELS_PATH, 'donor_model.pkl')
    DEMAND_MODEL_PATH = os.path.join(ML_MODELS_PATH, 'demand_model.pkl')
    
    # Logging
    LOG_PATH = os.path.join(os.getcwd(), 'logs')
    LOG_LEVEL = 'INFO'
    LOG_MAX_BYTES = 10240
    LOG_BACKUP_COUNT = 10
    
    # API Rate Limiting
    RATELIMIT_ENABLED = True
    RATELIMIT_DEFAULT = "100/hour"
    RATELIMIT_STORAGE_URL = "memory://"
    
    # Cache
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300
    
    @staticmethod
    def init_app(app):
        """Initialize application with this config"""
        # Create required directories
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.makedirs(app.config['CERTIFICATE_FOLDER'], exist_ok=True)
        os.makedirs(app.config['ML_MODELS_PATH'], exist_ok=True)
        os.makedirs(app.config['LOG_PATH'], exist_ok=True)