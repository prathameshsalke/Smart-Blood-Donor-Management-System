"""
Application Factory Module
Creates and configures the Flask application
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app(config_class=None):
    """
    Application factory function
    """
    app = Flask(__name__, 
                static_folder='static',
                template_folder='templates')
    
    # Load configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///blood_donor.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Upload folders
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/uploads')
    app.config['CERTIFICATE_FOLDER'] = os.path.join(app.root_path, 'static/certificates')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    # Create upload directories
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['CERTIFICATE_FOLDER'], exist_ok=True)
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    CORS(app)
    
    # Configure login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Setup logging
    setup_logging(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Create database tables
    with app.app_context():
        db.create_all()
        create_initial_admin()
    
    return app

def setup_logging(app):
    """Configure application logging"""
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    file_handler = RotatingFileHandler('logs/blood_donor.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Blood Donor Management System startup')

def register_blueprints(app):
    """Register all application blueprints"""
    
    # Import blueprints
    from app.blueprints.auth.routes import auth_bp
    from app.blueprints.donor.routes import donor_bp
    from app.blueprints.admin.routes import admin_bp
    from app.blueprints.api.routes import api_bp
    
    # Register blueprints with URL prefixes
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(donor_bp, url_prefix='/donor')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Register main routes
    from app.blueprints.main import register_main_routes
    register_main_routes(app)

def create_initial_admin():
    """Create initial admin user if not exists"""
    from app.models.user import User
    from werkzeug.security import generate_password_hash
    
    admin_email = os.environ.get('ADMIN_EMAIL', 'admin@blooddonor.com')
    admin_password = os.environ.get('ADMIN_PASSWORD', 'Admin@123')
    
    admin = User.query.filter_by(email=admin_email, role='admin').first()
    if not admin:
        admin = User(
            email=admin_email,
            password=generate_password_hash(admin_password),
            name='System Administrator',
            role='admin',
            is_active=True
        )
        db.session.add(admin)
        db.session.commit()
        print(f"Initial admin created: {admin_email}")