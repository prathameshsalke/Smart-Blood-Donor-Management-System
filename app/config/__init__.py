"""
Configuration module
"""

from .base import Config
from .development import DevelopmentConfig
from .production import ProductionConfig

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config(config_name=None):
    """Get configuration by name"""
    if config_name is None:
        import os
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    return config.get(config_name, config['default'])