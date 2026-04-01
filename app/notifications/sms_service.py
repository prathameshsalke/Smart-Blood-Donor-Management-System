"""
SMS Service - Handle SMS notifications
"""

import requests
import json
from flask import current_app
from app.utils.logger import logger

class SMSService:
    """Service for sending SMS messages"""
    
    @staticmethod
    def send_sms(phone_number, message):
        """Send SMS message"""
        try:
            # Get SMS configuration
            sms_provider = current_app.config.get('SMS_PROVIDER', 'twilio')
            
            if sms_provider == 'twilio':
                return SMSService._send_via_twilio(phone_number, message)
            elif sms_provider == 'msg91':
                return SMSService._send_via_msg91(phone_number, message)
            elif sms_provider == 'textlocal':
                return SMSService._send_via_textlocal(phone_number, message)
            else:
                # Log message for development
                logger.info(f"[SMS] To: {phone_number}, Message: {message}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to send SMS to {phone_number}: {str(e)}")
            return False
    
    @staticmethod
    def _send_via_twilio(phone_number, message):
        """Send SMS using Twilio"""
        try:
            account_sid = current_app.config.get('TWILIO_ACCOUNT_SID')
            auth_token = current_app.config.get('TWILIO_AUTH_TOKEN')
            from_number = current_app.config.get('TWILIO_PHONE_NUMBER')
            
            if not all([account_sid, auth_token, from_number]):
                logger.warning("Twilio credentials not configured")
                return False
            
            from twilio.rest import Client
            client = Client(account_sid, auth_token)
            
            client.messages.create(
                body=message,
                from_=from_number,
                to=phone_number
            )
            
            logger.info(f"SMS sent via Twilio to {phone_number}")
            return True
            
        except ImportError:
            logger.error("Twilio library not installed")
            return False
        except Exception as e:
            logger.error(f"Twilio error: {str(e)}")
            return False
    
    @staticmethod
    def _send_via_msg91(phone_number, message):
        """Send SMS using MSG91"""
        try:
            auth_key = current_app.config.get('MSG91_AUTH_KEY')
            sender_id = current_app.config.get('MSG91_SENDER_ID', 'BLOOD')
            route = current_app.config.get('MSG91_ROUTE', '4')
            
            if not auth_key:
                logger.warning("MSG91 credentials not configured")
                return False
            
            url = "https://api.msg91.com/api/sendhttp.php"
            params = {
                'authkey': auth_key,
                'mobiles': phone_number,
                'message': message,
                'sender': sender_id,
                'route': route,
                'country': '91'
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                logger.info(f"SMS sent via MSG91 to {phone_number}")
                return True
            else:
                logger.error(f"MSG91 error: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"MSG91 error: {str(e)}")
            return False
    
    @staticmethod
    def _send_via_textlocal(phone_number, message):
        """Send SMS using Textlocal"""
        try:
            api_key = current_app.config.get('TEXTLOCAL_API_KEY')
            sender = current_app.config.get('TEXTLOCAL_SENDER', 'BLOOD')
            
            if not api_key:
                logger.warning("Textlocal credentials not configured")
                return False
            
            url = "https://api.textlocal.in/send/"
            params = {
                'apikey': api_key,
                'numbers': phone_number,
                'message': message,
                'sender': sender
            }
            
            response = requests.post(url, data=params)
            if response.status_code == 200:
                logger.info(f"SMS sent via Textlocal to {phone_number}")
                return True
            else:
                logger.error(f"Textlocal error: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Textlocal error: {str(e)}")
            return False
    
    @staticmethod
    def send_emergency_alert(phone_number, blood_type, patient_name, location):
        """Send emergency alert SMS"""
        message = f"🚨 EMERGENCY: Blood needed - {blood_type} for {patient_name} at {location}. Please respond immediately."
        return SMSService.send_sms(phone_number, message)
    
    @staticmethod
    def send_donation_reminder(phone_number, donor_name, days_until):
        """Send donation reminder SMS"""
        message = f"Hi {donor_name}, you can donate blood again in {days_until} days. Thank you for saving lives!"
        return SMSService.send_sms(phone_number, message)
    
    @staticmethod
    def send_bulk_sms(phone_numbers, message):
        """Send SMS to multiple recipients"""
        success_count = 0
        for phone in phone_numbers:
            if SMSService.send_sms(phone, message):
                success_count += 1
        return success_count