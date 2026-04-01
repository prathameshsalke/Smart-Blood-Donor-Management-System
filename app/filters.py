"""
Custom Jinja2 filters for templates
"""

from datetime import datetime

def current_year():
    """Return the current year as a function (for templates that call it)"""
    return datetime.now().year

def register_filters(app):
    """Register all custom filters with the app"""
    app.jinja_env.globals.update(
        current_year=current_year  # This is a function
    )
