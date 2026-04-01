#!/usr/bin/env python
"""
Script to add messages table to database
Run: python scripts/add_messages_table.py
"""

import sys
import os

# Add the project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app import create_app, db
    from app.models.message import Message
    print("✅ Imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("\nCurrent Python path:")
    for path in sys.path:
        print(f"  - {path}")
    sys.exit(1)

def add_messages_table():
    """Create messages table in database"""
    app = create_app()
    
    with app.app_context():
        print("="*60)
        print("📝 ADDING MESSAGES TABLE")
        print("="*60)
        
        # Create tables
        db.create_all()
        print("✅ Database tables created/updated")
        
        # Verify table exists
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        print(f"\n📊 Tables in database: {', '.join(tables)}")
        
        if 'messages' in tables:
            print("✅ 'messages' table created successfully")
            
            # Check if there are any messages
            from app.models.message import Message
            message_count = Message.query.count()
            print(f"📧 Messages in database: {message_count}")
        else:
            print("❌ Failed to create 'messages' table")

def create_test_message():
    """Create a test message to verify table works"""
    app = create_app()
    
    with app.app_context():
        from app.models.user import User
        from app.models.message import Message
        from app.services.message_service import MessageService
        
        # Get first donor
        donor = User.query.filter_by(role='donor').first()
        
        if donor:
            # Create test message
            message = MessageService.send_message(
                recipient_id=donor.id,
                subject="📝 Test Message",
                content="This is a test message to verify the messages table is working correctly.",
                message_type='notification'
            )
            
            print(f"\n✅ Test message created:")
            print(f"  Message ID: {message.message_id}")
            print(f"  To: {donor.name}")
            print(f"  Subject: {message.subject}")
        else:
            print("\n⚠️ No donors found to create test message")

if __name__ == "__main__":
    add_messages_table()
    create_test_message()