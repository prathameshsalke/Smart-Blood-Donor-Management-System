"""
Notification Service for sending alerts and notifications
"""

import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app, url_for
from datetime import datetime

class NotificationService:
    """Service for sending notifications via email, SMS, etc."""
    
    @classmethod
    def send_email(cls, to_email, subject, body, html_body=None):
        """
        Send email notification
        """
        try:
            # Get email configuration from environment
            smtp_server = current_app.config.get('MAIL_SERVER', 'smtp.gmail.com')
            smtp_port = current_app.config.get('MAIL_PORT', 587)
            smtp_username = current_app.config.get('MAIL_USERNAME')
            smtp_password = current_app.config.get('MAIL_PASSWORD')
            from_email = current_app.config.get('MAIL_DEFAULT_SENDER', smtp_username)
            
            if not smtp_username or not smtp_password:
                current_app.logger.warning("Email not configured. Skipping notification.")
                return False
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Attach plain text
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach HTML if provided
            if html_body:
                msg.attach(MIMEText(html_body, 'html'))
            
            # Send email
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
            server.quit()
            
            current_app.logger.info(f"Email sent to {to_email}")
            return True
            
        except Exception as e:
            current_app.logger.error(f"Email sending error: {e}")
            return False
    
    @classmethod
    def send_sms(cls, phone_number, message):
        """
        Send SMS notification (using Twilio or similar service)
        """
        try:
            # This would integrate with SMS gateway like Twilio
            # For now, log the message
            current_app.logger.info(f"SMS to {phone_number}: {message}")
            
            # Example with Twilio (commented out)
            """
            from twilio.rest import Client
            
            account_sid = current_app.config.get('TWILIO_ACCOUNT_SID')
            auth_token = current_app.config.get('TWILIO_AUTH_TOKEN')
            twilio_phone = current_app.config.get('TWILIO_PHONE_NUMBER')
            
            if account_sid and auth_token:
                client = Client(account_sid, auth_token)
                client.messages.create(
                    body=message,
                    from_=twilio_phone,
                    to=phone_number
                )
            """
            
            return True
            
        except Exception as e:
            current_app.logger.error(f"SMS sending error: {e}")
            return False
    
    @classmethod
    def send_emergency_alert(cls, donor, blood_request, distance):
        """
        Send emergency alert to a donor
        """
        try:
            # Prepare notification content
            subject = f"🚨 EMERGENCY Blood Request - {blood_request.blood_type_needed}"
            
            body = f"""
            EMERGENCY BLOOD REQUEST
            
            Blood Type Needed: {blood_request.blood_type_needed}
            Patient: {blood_request.patient_name}
            Hospital: {blood_request.hospital_name or 'Contact for details'}
            Your Distance: {distance} km
            
            This is an emergency request. Please respond immediately if you can donate.
            
            To respond, please login to your account:
            {current_app.config.get('APP_URL', 'http://localhost:5000')}/donor/dashboard
            """
            
            html_body = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
                <div style="background-color: #ff4444; color: white; padding: 10px; text-align: center; border-radius: 5px 5px 0 0;">
                    <h1>🚨 EMERGENCY BLOOD REQUEST</h1>
                </div>
                <div style="padding: 20px;">
                    <h2>Blood Type Needed: <span style="color: #ff4444;">{blood_request.blood_type_needed}</span></h2>
                    <p><strong>Patient:</strong> {blood_request.patient_name}</p>
                    <p><strong>Hospital:</strong> {blood_request.hospital_name or 'Contact for details'}</p>
                    <p><strong>Your Distance:</strong> {distance} km</p>
                    <p><strong>Urgency:</strong> <span style="color: #ff4444;">EMERGENCY</span></p>
                    
                    <div style="background-color: #f8f9fa; padding: 15px; margin: 20px 0; border-left: 4px solid #ff4444;">
                        <p style="margin: 0;"><strong>Dear {donor.user.name},</strong></p>
                        <p>This is an emergency request. Your blood type matches what's urgently needed.</p>
                    </div>
                    
                    <a href="{current_app.config.get('APP_URL', 'http://localhost:5000')}/donor/respond/{blood_request.request_id}" 
                       style="display: inline-block; background-color: #28a745; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; margin: 10px 0;">
                        I Can Donate
                    </a>
                    
                    <p style="color: #666; margin-top: 20px;">
                        Please respond as quickly as possible. Lives depend on it.
                    </p>
                </div>
            </div>
            """
            
            # Send via both email and SMS for emergency
            email_sent = False
            sms_sent = False
            
            if donor.user.email:
                email_sent = cls.send_email(
                    donor.user.email, 
                    subject, 
                    body, 
                    html_body
                )
            
            if donor.user.phone:
                sms_body = f"EMERGENCY: Blood needed {blood_request.blood_type_needed}. Patient: {blood_request.patient_name}. Distance: {distance}km. Please login to respond."
                sms_sent = cls.send_sms(donor.user.phone, sms_body)
            
            return email_sent or sms_sent
            
        except Exception as e:
            current_app.logger.error(f"Emergency alert error: {e}")
            return False
    
    @classmethod
    def send_request_update(cls, donor, blood_request, status):
        """
        Send update about blood request status
        """
        try:
            subject = f"Blood Request Update - {blood_request.request_id}"
            
            body = f"""
            Blood Request Update
            
            Request ID: {blood_request.request_id}
            Patient: {blood_request.patient_name}
            Blood Type: {blood_request.blood_type_needed}
            Status: {status}
            
            Thank you for your willingness to donate blood.
            """
            
            if donor.user.email:
                cls.send_email(donor.user.email, subject, body)
            
        except Exception as e:
            current_app.logger.error(f"Request update error: {e}")
    
    @classmethod
    def send_donation_reminder(cls, donor):
        """
        Send reminder to donor about upcoming eligibility
        """
        try:
            if not donor.last_donation_date:
                return
            
            from datetime import datetime, timedelta
            next_eligible = donor.last_donation_date + timedelta(days=90)
            days_until = (next_eligible - datetime.now()).days
            
            if days_until <= 7:  # Remind when 7 days left
                subject = "You Can Donate Blood Again Soon!"
                
                body = f"""
                Dear {donor.user.name},
                
                You will be eligible to donate blood again in {days_until} days.
                Your last donation was on {donor.last_donation_date.strftime('%B %d, %Y')}.
                
                Please consider scheduling your next donation to help save lives.
                
                Login to your account to update your availability:
                {current_app.config.get('APP_URL', 'http://localhost:5000')}/donor/dashboard
                
                Thank you for being a lifesaver!
                """
                
                if donor.user.email:
                    cls.send_email(donor.user.email, subject, body)
                    
        except Exception as e:
            current_app.logger.error(f"Reminder error: {e}")