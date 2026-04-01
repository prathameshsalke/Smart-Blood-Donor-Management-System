"""
Message Service for handling donor messages and notifications
"""

from app import db
from app.models.message import Message
from app.models.user import User
from app.services.email_service import EmailService
from datetime import datetime
from flask import url_for

class MessageService:
    """Service for managing messages and notifications"""
    
    @staticmethod
    def send_message(recipient_id, subject, content, message_type='notification', 
                    sender_id=None, related_donation_id=None, related_request_id=None):
        """Send a message to a donor"""
        message = Message(
            recipient_id=recipient_id,
            sender_id=sender_id,
            subject=subject,
            content=content,
            message_type=message_type,
            related_donation_id=related_donation_id,
            related_request_id=related_request_id
        )
        db.session.add(message)
        db.session.commit()
        
        # Send email notification
        recipient = User.query.get(recipient_id)
        if recipient and recipient.email:
            EmailService.send_notification(
                recipient.email,
                subject,
                content
            )
        
        return message
    
    @staticmethod
    def get_unread_count(user_id):
        """Get count of unread messages for a user"""
        return Message.query.filter_by(
            recipient_id=user_id,
            is_read=False,
            is_archived=False
        ).count()
    
    @staticmethod
    def get_messages(user_id, page=1, per_page=20, message_type=None):
        """Get messages for a user with pagination"""
        query = Message.query.filter_by(
            recipient_id=user_id,
            is_archived=False
        )
        
        if message_type:
            query = query.filter_by(message_type=message_type)
        
        return query.order_by(Message.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
    
    @staticmethod
    def get_recent_messages(user_id, limit=5):
        """Get recent messages for dashboard preview"""
        return Message.query.filter_by(
            recipient_id=user_id,
            is_archived=False
        ).order_by(Message.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def mark_as_read(message_id, user_id):
        """Mark a message as read"""
        message = Message.query.filter_by(
            message_id=message_id,
            recipient_id=user_id
        ).first()
        
        if message:
            message.mark_as_read()
            return True
        return False
    
    @staticmethod
    def mark_all_as_read(user_id):
        """Mark all messages as read for a user"""
        Message.query.filter_by(
            recipient_id=user_id,
            is_read=False
        ).update({'is_read': True, 'read_at': datetime.utcnow()})
        db.session.commit()
        return True
    
    @staticmethod
    def archive_message(message_id, user_id):
        """Archive a message"""
        message = Message.query.filter_by(
            message_id=message_id,
            recipient_id=user_id
        ).first()
        
        if message:
            message.is_archived = True
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def delete_message(message_id, user_id):
        """Permanently delete a message"""
        message = Message.query.filter_by(
            message_id=message_id,
            recipient_id=user_id
        ).first()
        
        if message:
            db.session.delete(message)
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def send_certificate_notification(donation):
        """Send certificate generation notification"""
        subject = f"🎉 Donation Certificate Ready - {donation.donation_id}"
        content = f"""
        Dear {donation.donor_name},
        
        Your blood donation certificate has been generated and is now available in your dashboard.
        
        Donation Details:
        • Donation ID: {donation.donation_id}
        • Date: {donation.donation_date.strftime('%B %d, %Y at %I:%M %p')}
        • Blood Type: {donation.donor_blood_type}
        • Units Donated: {donation.units_donated}
        
        You can download your certificate from:
        • Your donor dashboard
        • Donation history page
        
        Thank you for saving lives!
        
        - Smart Blood Donor Team
        """
        
        return MessageService.send_message(
            recipient_id=donation.donor_id,
            subject=subject,
            content=content,
            message_type='certificate',
            related_donation_id=donation.donation_id
        )
    
    @staticmethod
    def send_request_notification(blood_request, donor_ids):
        """Send blood request notifications to matching donors"""
        notifications_sent = []
        
        for donor_id in donor_ids:
            subject = f"🚨 Blood Request: {blood_request.blood_type_needed} Needed"
            content = f"""
            A blood request matching your profile has been posted!
            
            Request Details:
            • Blood Type Needed: {blood_request.blood_type_needed}
            • Patient: {blood_request.patient_name}
            • Hospital: {blood_request.hospital_name or 'Not specified'}
            • Urgency: {blood_request.urgency.upper()}
            • Units Required: {blood_request.units_needed}
            
            Please log in to your dashboard to respond to this request.
            
            - Smart Blood Donor Team
            """
            
            message = MessageService.send_message(
                recipient_id=donor_id,
                subject=subject,
                content=content,
                message_type='request',
                related_request_id=blood_request.request_id
            )
            notifications_sent.append(message)
        
        return notifications_sent
    
    @staticmethod
    def send_contact_message(sender_id, recipient_id, message_content):
        """Send a contact message between donors"""
        sender = User.query.get(sender_id)
        recipient = User.query.get(recipient_id)
        
        if not sender or not recipient:
            return None
        
        subject = f"📬 Contact Message from {sender.name}"
        content = f"""
        You have received a contact message from {sender.name} ({sender.email}).
        
        Message:
        {message_content}
        
        You can reply to this message or contact them directly:
        • Phone: {sender.phone}
        • Email: {sender.email}
        
        Login to your dashboard to view all messages: {url_for('donor.messages', _external=True)}
        
        - Smart Blood Donor System
        """
        
        return MessageService.send_message(
            recipient_id=recipient_id,
            subject=subject,
            content=content,
            message_type='contact',
            sender_id=sender_id
        )
    
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
    def send_daily_greeting(user_id, user_name, stats):
        """Send daily greeting message"""
        from datetime import datetime
        
        hour = datetime.now().hour
        if hour < 12:
            greeting = "🌅 Good Morning"
            emoji = "☀️"
        elif hour < 17:
            greeting = "☀️ Good Afternoon"
            emoji = "⛅"
        else:
            greeting = "🌙 Good Evening"
            emoji = "✨"
        
        subject = f"{greeting}, {user_name}! - Your Daily Update"
        
        content = f"""
{emoji} {greeting}, {user_name}!

📊 **Today's Quick Stats:**
• Total donors in your area: {stats.get('nearby_donors', 0)}
• Active blood requests: {stats.get('active_requests', 0)}
• Your total donations: {stats.get('user_donations', 0)}

💝 **Today's Donation Tip:**
Stay hydrated and eat iron-rich foods to maintain healthy hemoglobin levels.

👉 Visit your dashboard to check for nearby donation opportunities.

Have a wonderful day!
The Smart Blood Donor Team
"""
        
        return MessageService.send_message(
            recipient_id=user_id,
            subject=subject,
            content=content,
            message_type='daily_greeting'
        )