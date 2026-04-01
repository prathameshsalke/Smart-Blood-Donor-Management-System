"""
Welcome Message Service - Handles welcome messages and daily greetings
"""

from app import db
from app.models.user import User
from app.models.message import Message
from app.services.message_service import MessageService
from datetime import datetime, time
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

class WelcomeService:
    """Service for welcome messages and daily greetings"""
    
    @staticmethod
    def send_welcome_message(user_id, user_name):
        """Send welcome message to new donor"""
        subject = "🎉 Welcome to Smart Blood Donor System!"
        content = f"""
Dear {user_name},

Welcome to the Smart Blood Donor System! We're thrilled to have you as part of our life-saving community.

✨ **What You Can Do Now:**
• Complete your donor profile with photo and location
• Check your donation eligibility status
• Find nearby blood donation opportunities
• Receive notifications for emergency requests
• Track your donation history and download certificates

🩸 **Getting Started:**
1. Update your profile photo and location
2. Check your eligibility status
3. Browse nearby blood requests
4. Spread the word - share your donor profile!

📱 **Stay Connected:**
You'll receive notifications for:
• Emergency blood requests in your area
• Your donation certificates
• Eligibility reminders
• Daily greetings and updates

Remember, every donation can save up to 3 lives. Thank you for joining us in this noble cause!

If you have any questions, feel free to contact our support team.

With gratitude,
The Smart Blood Donor Team
"""
        
        return MessageService.send_message(
            recipient_id=user_id,
            subject=subject,
            content=content,
            message_type='welcome'
        )
    
    @staticmethod
    def send_daily_greeting():
        """Send daily good morning message to all donors"""
        from app import create_app
        app = create_app()
        
        with app.app_context():
            # Get all active donors
            donors = User.query.filter_by(role='donor', is_active=True).all()
            
            # Time-based greeting
            current_hour = datetime.now().hour
            
            if current_hour < 12:
                greeting = "🌅 Good Morning"
                emoji = "☀️"
            elif current_hour < 17:
                greeting = "☀️ Good Afternoon"
                emoji = "⛅"
            else:
                greeting = "🌙 Good Evening"
                emoji = "✨"
            
            subject = f"{greeting} - Your Daily Blood Donor Update"
            
            # Donation fact of the day
            donation_facts = [
                "🩸 Every 2 seconds someone needs blood in India.",
                "🏥 One blood donation can save up to 3 lives.",
                "❤️ Regular blood donation reduces the risk of heart disease.",
                "📅 You can donate blood every 90 days.",
                "🆎 O Negative is the universal blood type - always in demand!",
                "💪 Donating blood burns about 650 calories.",
                "🎁 Platelets can be donated every 7 days, up to 24 times a year.",
                "🩺 Your body replaces plasma within 24 hours of donation.",
                "⚡ Red blood cells take about 4-6 weeks to fully replace.",
                "🌟 Only 1% of Indians donate blood - be part of the 1%!"
            ]
            
            fact = donation_facts[datetime.now().day % len(donation_facts)]
            
            for donor in donors:
                content = f"""
{emoji} {greeting}, {donor.name}!

{fact}

📊 **Today's Quick Stats:**
• Total donors in our community: {User.query.filter_by(role='donor').count()}
• Current blood requests: {get_blood_request_count()}
• Your total donations: {get_donor_donations(donor.id)}

💝 **Today's Donation Tip:**
Stay hydrated and eat iron-rich foods to maintain healthy hemoglobin levels.

👉 Visit your dashboard to check for nearby donation opportunities.

Have a wonderful day!
The Smart Blood Donor Team
"""
                
                MessageService.send_message(
                    recipient_id=donor.id,
                    subject=subject,
                    content=content,
                    message_type='daily_greeting'
                )
            
            print(f"✅ Daily greetings sent to {len(donors)} donors at {datetime.now().strftime('%H:%M')}")
            return len(donors)

def get_blood_request_count():
    """Get count of pending blood requests"""
    from app.models.blood_request import BloodRequest
    return BloodRequest.query.filter_by(status='pending').count()

def get_donor_donations(user_id):
    """Get total donations for a donor"""
    from app.models.donation import Donation
    return Donation.query.filter_by(donor_id=user_id).count()

# Initialize scheduler for daily messages
scheduler = BackgroundScheduler()

# Schedule daily greeting at 8:00 AM
scheduler.add_job(
    func=WelcomeService.send_daily_greeting,
    trigger="cron",
    hour=8,
    minute=0,
    id="daily_greeting"
)

# Start scheduler
scheduler.start()

# Shut down scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())