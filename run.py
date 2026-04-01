#!/usr/bin/env python3
"""
Smart Blood Donor Management System - Entry Point
Run this file to start the application
"""

import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 5000))
    
    # Run the app with debug mode based on environment
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    
    app.run(
        host='0.0.0.0',  # Make server publicly available
        port=port,
        debug=debug_mode
    )