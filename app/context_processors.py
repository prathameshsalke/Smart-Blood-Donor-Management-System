# app/context_processors.py
from datetime import datetime

def inject_now():
    """Inject current datetime into template context"""
    return {'now': datetime.now()}