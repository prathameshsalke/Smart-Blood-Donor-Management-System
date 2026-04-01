# tests/test_welcome.py
"""
Test script for welcome messages and daily greetings
Run: python tests/test_welcome.py
"""

import sys
import os

# Add the project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app import create_app
    from app.services.welcome_service import WelcomeService
    from app.models.user import User
    print("✅ Imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("\nCurrent Python path:")
    for path in sys.path:
        print(f"  - {path}")
    sys.exit(1)

def test_welcome_message():
    """Test sending welcome message to a donor"""
    app = create_app()
    
    with app.app_context():
        print("="*60)
        print("📧 TESTING WELCOME MESSAGE")
        print("="*60)
        
        # Get first donor
        donor = User.query.filter_by(role='donor').first()
        
        if donor:
            print(f"✓ Found donor: {donor.name} (ID: {donor.id})")
            
            # Send welcome message
            result = WelcomeService.send_welcome_message(donor.id, donor.name)
            
            if result:
                print("✓ Welcome message sent successfully")
                print(f"  Message ID: {result.message_id}")
                print(f"  Subject: {result.subject}")
            else:
                print("✗ Failed to send welcome message")
        else:
            print("✗ No donors found in database")

def test_daily_greeting():
    """Test sending daily greeting"""
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*60)
        print("☀️ TESTING DAILY GREETING")
        print("="*60)
        
        # Send daily greeting
        count = WelcomeService.send_daily_greeting()
        
        print(f"✓ Daily greeting sent to {count} donors")

if __name__ == "__main__":
    test_welcome_message()
    test_daily_greeting()