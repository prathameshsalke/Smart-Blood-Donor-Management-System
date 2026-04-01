"""
Email Service - Handle email notifications
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app, render_template
from app.utils.logger import logger

class EmailService:
    """Service for sending emails"""
    
    @staticmethod
    def send_email(to_email, subject, template, **kwargs):
        """Send email using template"""
        try:
            # Get email configuration
            smtp_server = current_app.config.get('MAIL_SERVER', 'smtp.gmail.com')
            smtp_port = current_app.config.get('MAIL_PORT', 587)
            smtp_username = current_app.config.get('MAIL_USERNAME')
            smtp_password = current_app.config.get('MAIL_PASSWORD')
            from_email = current_app.config.get('MAIL_DEFAULT_SENDER', smtp_username)
            
            if not smtp_username or not smtp_password:
                logger.warning("Email not configured. Skipping notification.")
                return False
            
            # Render email templates
            html_body = render_template(f'emails/{template}.html', **kwargs)
            text_body = render_template(f'emails/{template}.txt', **kwargs)
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Attach parts
            msg.attach(MIMEText(text_body, 'plain'))
            msg.attach(MIMEText(html_body, 'html'))
            
            # Send email
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    @staticmethod
    def send_welcome_email(user):
        """Send welcome email to new user"""
        return EmailService.send_email(
            to_email=user.email,
            subject="Welcome to Smart Blood Donor System",
            template="welcome",
            user=user
        )
    
    @staticmethod
    def send_donation_confirmation(donation):
        """Send donation confirmation email"""
        return EmailService.send_email(
            to_email=donation.donor.email,
            subject="Thank You for Your Blood Donation",
            template="donation_confirmation",
            donation=donation
        )
    
    @staticmethod
    def send_emergency_alert(donor, request):
        """Send emergency alert email"""
        return EmailService.send_email(
            to_email=donor.user.email,
            subject=f"🚨 EMERGENCY: Blood Needed - {request.blood_type_needed}",
            template="emergency_alert",
            donor=donor,
            request=request
        )
    
    @staticmethod
    def send_request_update(donor, request, status):
        """Send request update email"""
        return EmailService.send_email(
            to_email=donor.user.email,
            subject=f"Blood Request Update - {request.request_id}",
            template="request_update",
            donor=donor,
            request=request,
            status=status
        )
    
    @staticmethod
    def send_eligibility_reminder(donor, days_left):
        """Send eligibility reminder email"""
        return EmailService.send_email(
            to_email=donor.user.email,
            subject="You Can Donate Blood Again Soon!",
            template="eligibility_reminder",
            donor=donor,
            days_left=days_left
        )
    
    @staticmethod
    def send_bulk_emails(recipients, subject, template, **kwargs):
        """Send emails to multiple recipients"""
        success_count = 0
        for recipient in recipients:
            if EmailService.send_email(recipient, subject, template, **kwargs):
                success_count += 1
        return success_count