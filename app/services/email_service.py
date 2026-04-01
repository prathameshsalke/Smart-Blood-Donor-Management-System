"""
Email Service for sending email notifications
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app, url_for
import logging

class EmailService:
    """Service for sending emails"""
    
    @staticmethod
    def send_email(to_email, subject, body, html_body=None):
        """Send email"""
        try:
            # Get email configuration
            smtp_server = current_app.config.get('MAIL_SERVER', 'smtp.gmail.com')
            smtp_port = current_app.config.get('MAIL_PORT', 587)
            smtp_username = current_app.config.get('MAIL_USERNAME')
            smtp_password = current_app.config.get('MAIL_PASSWORD')
            from_email = current_app.config.get('MAIL_DEFAULT_SENDER', smtp_username)
            
            # Log email attempt (useful for debugging)
            logging.info(f"Attempting to send email to {to_email} with subject: {subject}")
            
            # Check if email is configured
            if not smtp_username or not smtp_password:
                logging.warning("Email not configured. Skipping notification.")
                # For development, just log the email
                logging.info(f"DEV MODE - Email would be sent to: {to_email}")
                logging.info(f"Subject: {subject}")
                logging.info(f"Body: {body}")
                return True
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Attach plain text version
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach HTML version if provided
            if html_body:
                msg.attach(MIMEText(html_body, 'html'))
            
            # Send email
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
            server.quit()
            
            logging.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logging.error(f"Email error: {e}")
            return False
    
    @staticmethod
    def send_certificate_notification(donation):
        """Send certificate notification email"""
        subject = f"🎉 Your Blood Donation Certificate is Ready - {donation.donation_id}"
        
        body = f"""
Dear {donation.donor_name},

Your blood donation certificate has been generated and is now available.

Donation Details:
• Donation ID: {donation.donation_id}
• Date: {donation.donation_date.strftime('%B %d, %Y at %I:%M %p')}
• Blood Type: {donation.donor_blood_type}
• Units: {donation.units_donated}

You can download your certificate from your donor dashboard.

Thank you for saving lives!

- Smart Blood Donor Team
"""
        
        html_body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: #dc3545; color: white; padding: 20px; text-align: center;">
                <h1>Blood Donation Certificate</h1>
            </div>
            <div style="padding: 20px;">
                <h2>Dear {donation.donor_name},</h2>
                <p>Your blood donation certificate has been generated and is now available.</p>
                
                <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="color: #dc3545;">Donation Details:</h3>
                    <p><strong>Donation ID:</strong> {donation.donation_id}</p>
                    <p><strong>Date:</strong> {donation.donation_date.strftime('%B %d, %Y at %I:%M %p')}</p>
                    <p><strong>Blood Type:</strong> {donation.donor_blood_type}</p>
                    <p><strong>Units Donated:</strong> {donation.units_donated}</p>
                </div>
                
                <p>You can download your certificate from your <a href="{url_for('donor.dashboard', _external=True)}" style="color: #dc3545;">donor dashboard</a>.</p>
                <p>Thank you for saving lives!</p>
                
                <p>Best regards,<br>Smart Blood Donor Team</p>
            </div>
        </div>
        """
        
        return EmailService.send_email(
            to_email=donation.donor.user.email,
            subject=subject,
            body=body,
            html_body=html_body
        )
    
    @staticmethod
    def send_notification(to_email, subject, message):
        """Send general notification email"""
        body = f"""
{message}

Thank you for being part of the Smart Blood Donor community!

- Smart Blood Donor Team
"""
        
        html_body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: #dc3545; color: white; padding: 10px 20px;">
                <h2 style="margin: 0;">Smart Blood Donor System</h2>
            </div>
            <div style="padding: 20px;">
                <p style="white-space: pre-line;">{message}</p>
                <hr style="border: 1px solid #eee;">
                <p style="color: #666; font-size: 12px;">
                    Thank you for being part of the Smart Blood Donor community!
                </p>
            </div>
        </div>
        """
        
        return EmailService.send_email(
            to_email=to_email,
            subject=subject,
            body=body,
            html_body=html_body
        )
    
    @staticmethod
    def send_contact_notification(sender, recipient, message):
        """Send email notification for contact message"""
        subject = f"New Contact Message from {sender.name} - Blood Donor System"
        
        body = f"""
Hello {recipient.name},

You have received a contact message from {sender.name} ({sender.email}).

Message:
{message}

You can reply to this email or contact them directly:
• Phone: {sender.phone}
• Email: {sender.email}

Login to your dashboard to view all messages: {url_for('donor.messages', _external=True)}

- Smart Blood Donor System
"""
        
        html_body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: #dc3545; color: white; padding: 20px; text-align: center;">
                <h2>New Contact Message</h2>
            </div>
            <div style="padding: 20px;">
                <p><strong>From:</strong> {sender.name} ({sender.email})</p>
                <p><strong>Message:</strong></p>
                <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0;">
                    {message.replace(chr(10), '<br>')}
                </div>
                
                <h3 style="color: #dc3545; margin-top: 20px;">Contact Information:</h3>
                <p><strong>Phone:</strong> <a href="tel:{sender.phone}" style="color: #dc3545;">{sender.phone}</a></p>
                <p><strong>Email:</strong> <a href="mailto:{sender.email}" style="color: #dc3545;">{sender.email}</a></p>
                
                <hr style="border: 1px solid #eee; margin: 20px 0;">
                <p><a href="{url_for('donor.messages', _external=True)}" style="background: #dc3545; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">View in Dashboard</a></p>
            </div>
        </div>
        """
        
        return EmailService.send_email(
            to_email=recipient.email,
            subject=subject,
            body=body,
            html_body=html_body
        )
    
    @staticmethod
    def send_welcome_email(user):
        """Send welcome email to new user"""
        subject = "🎉 Welcome to Smart Blood Donor System!"
        
        body = f"""
Dear {user.name},

Welcome to the Smart Blood Donor System! We're thrilled to have you as part of our life-saving community.

Your account has been successfully created. You can now:
• Complete your donor profile
• Find nearby blood donation opportunities
• Track your donation history
• Receive emergency alerts

Get started by logging in and updating your profile:
{url_for('donor.edit_profile', _external=True)}

Remember, every donation can save up to 3 lives!

If you have any questions, feel free to contact our support team.

Best regards,
The Smart Blood Donor Team
"""
        
        html_body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: #dc3545; color: white; padding: 20px; text-align: center;">
                <h1>🎉 Welcome to Smart Blood Donor System!</h1>
            </div>
            <div style="padding: 20px;">
                <h2>Dear {user.name},</h2>
                <p>Welcome to the Smart Blood Donor System! We're thrilled to have you as part of our life-saving community.</p>
                
                <p>Your account has been successfully created. You can now:</p>
                <ul>
                    <li>✅ Complete your donor profile</li>
                    <li>✅ Find nearby blood donation opportunities</li>
                    <li>✅ Track your donation history</li>
                    <li>✅ Receive emergency alerts</li>
                </ul>
                
                <p style="text-align: center; margin: 30px 0;">
                    <a href="{url_for('donor.edit_profile', _external=True)}" 
                       style="background: #dc3545; color: white; padding: 12px 30px; text-decoration: none; border-radius: 25px;">
                        Get Started Now
                    </a>
                </p>
                
                <p>Remember, every donation can save up to 3 lives!</p>
                <p>If you have any questions, feel free to contact our support team.</p>
                
                <p>Best regards,<br>The Smart Blood Donor Team</p>
            </div>
        </div>
        """
        
        return EmailService.send_email(
            to_email=user.email,
            subject=subject,
            body=body,
            html_body=html_body
        )