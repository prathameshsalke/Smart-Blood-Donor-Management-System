"""
Auth Blueprint - Initialize authentication routes
"""

from flask import Blueprint

auth_bp = Blueprint('auth', __name__, 
                    template_folder='../templates/auth',
                    static_folder='../static',
                    url_prefix='/auth')

# Import routes at bottom to avoid circular imports
from . import routes
from . import forms