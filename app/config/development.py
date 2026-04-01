"""
Development configuration
"""

from .base import Config
import os

class DevelopmentConfig(Config):
    """Development configuration"""
    
    DEBUG = True
    TESTING = False
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DEV_DATABASE_URL', 
        'sqlite:///instance/blood_donor_dev.db'
    )
    
    # Debug toolbar
    DEBUG_TB_ENABLED = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    
    # Mail settings (use console for development)
    MAIL_SERVER = 'localhost'
    MAIL_PORT = 1025
    MAIL_USE_TLS = False
    MAIL_USERNAME = None
    MAIL_PASSWORD = None
    
    # Logging
    LOG_LEVEL = 'DEBUG'
    
    # Rate limiting (disabled in development)
    RATELIMIT_ENABLED = False
    
    @staticmethod
    def init_app(app):
        """Initialize development app"""
        Config.init_app(app)
        
        # Enable debug toolbar
        from flask_debugtoolbar import DebugToolbarExtension
        toolbar = DebugToolbarExtension()
        toolbar.init_app(app)
        
        print("Running in DEVELOPMENT mode")