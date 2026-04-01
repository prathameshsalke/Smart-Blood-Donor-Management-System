"""
Donor Blueprint - Initialize donor routes
"""

from flask import Blueprint

donor_bp = Blueprint('donor', __name__, 
                     template_folder='../templates/donor',
                     static_folder='../static',
                     url_prefix='/donor')

# Import routes at bottom to avoid circular imports
from . import routes