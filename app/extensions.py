"""
Extensions module - Initialize Flask extensions
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_cors import CORS
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Database
db = SQLAlchemy()

# Authentication
login_manager = LoginManager()

# Database migrations
migrate = Migrate()

# Cross-Origin Resource Sharing
cors = CORS()

# CSRF Protection
csrf = CSRFProtect()

# Mail
mail = Mail()

# Caching
cache = Cache(config={'CACHE_TYPE': 'simple'})

# Rate Limiting
limiter = Limiter(key_func=get_remote_address)

# Configure login manager
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'