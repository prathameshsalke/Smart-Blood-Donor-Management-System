"""
Email Tasks - Background email sending
"""

import threading
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app, render_template
from app.utils.logger import logger

def send_email_async(app, to_email, subject, template, **kwargs):
    """Send email asynchronously"""
    with app.app_context():
        try:
            # Render email template
            html_body = render_template(f'emails/{template}.html', **kwargs)
            text_body = render_template(f'emails/{template}.txt', **kwargs)
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = current_app.config['MAIL_DEFAULT_SENDER']
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Attach parts
            msg.attach(MIMEText(text_body, 'plain'))
            msg.attach(MIMEText(html_body, 'html'))
            
            # Send email
            server = smtplib.SMTP(
                current_app.config['MAIL_SERVER'],
                current_app.config['MAIL_PORT']
            )
            server.starttls()
            server.login(
                current_app.config['MAIL_USERNAME'],
                current_app.config['MAIL_PASSWORD']
            )
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email sent successfully to {to_email}")
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")

def send_email(to_email, subject, template, **kwargs):
    """Send email (synchronous wrapper)"""
    from flask import current_app
    
    # Get app instance
    app = current_app._get_current_object()
    
    # Start thread
    thread = threading.Thread(
        target=send_email_async,
        args=(app, to_email, subject, template),
        kwargs=kwargs
    )
    thread.daemon = True
    thread.start()
    
    return True

def send_bulk_emails(recipients, subject, template, **kwargs):
    """Send bulk emails"""
    from flask import current_app
    
    app = current_app._get_current_object()
    
    def send_bulk():
        with app.app_context():
            for recipient in recipients:
                try:
                    send_email_async(app, recipient, subject, template, **kwargs)
                except Exception as e:
                    logger.error(f"Failed to send bulk email to {recipient}: {str(e)}")
    
    # Start thread
    thread = threading.Thread(target=send_bulk)
    thread.daemon = True
    thread.start()
    
    return True

def send_welcome_email(user):
    """Send welcome email to new user"""
    send_email(
        to_email=user.email,
        subject="Welcome to Smart Blood Donor System",
        template="welcome",
        user=user
    )

def send_donation_confirmation(donation):
    """Send donation confirmation email"""
    send_email(
        to_email=donation.donor.email,
        subject="Thank You for Your Blood Donation",
        template="donation_confirmation",
        donation=donation
    )

def send_emergency_alert_email(donor, request):
    """Send emergency alert email"""
    send_email(
        to_email=donor.user.email,
        subject=f"🚨 EMERGENCY: Blood Needed - {request.blood_type_needed}",
        template="emergency_alert",
        donor=donor,
        request=request
    )

def send_request_update_email(donor, request, status):
    """Send request update email"""
    send_email(
        to_email=donor.user.email,
        subject=f"Blood Request Update - {request.request_id}",
        template="request_update",
        donor=donor,
        request=request,
        status=status
    )

def send_eligibility_reminder(donor):
    """Send eligibility reminder email"""
    from datetime import datetime, timedelta
    
    if donor.last_donation_date:
        next_date = donor.last_donation_date + timedelta(days=90)
        days_left = (next_date - datetime.now()).days
        
        send_email(
            to_email=donor.user.email,
            subject="You Can Donate Blood Again Soon!",
            template="eligibility_reminder",
            donor=donor,
            days_left=days_left,
            next_date=next_date
        )