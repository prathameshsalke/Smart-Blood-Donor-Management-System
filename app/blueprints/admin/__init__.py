"""
Admin Blueprint - Initialize admin routes
"""

from flask import Blueprint

admin_bp = Blueprint('admin', __name__, 
                     template_folder='../templates/admin',
                     static_folder='../static',
                     url_prefix='/admin')

# Import routes at bottom to avoid circular imports
from . import routes