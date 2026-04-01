"""
API Blueprint - Initialize API routes
"""

from flask import Blueprint

api_bp = Blueprint('api', __name__, url_prefix='/api')

# Import all API route modules
from . import routes
from . import auth_api
from . import donor_api
from . import hospital_api
from . import emergency_api