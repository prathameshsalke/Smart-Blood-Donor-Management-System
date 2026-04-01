"""
Emergency Alert Tasks - Handle emergency notifications
"""

import threading
from flask import current_app
from app.services.geo_service import GeoService
from app.services.notification_service import NotificationService
from app.repositories.donor_repo import DonorRepository
from app.repositories.request_repo import BloodRequestRepository
from app.utils.logger import logger

def process_emergency_alerts_async(app, request_id):
    """Process emergency alerts asynchronously"""
    with app.app_context():
        try:
            # Get request
            request = BloodRequestRepository.get_by_id(request_id)
            if not request:
                logger.error(f"Emergency request {request_id} not found")
                return
            
            # Find nearby donors
            nearby_donors = GeoService.find_nearby_donors(
                request.requester_latitude,
                request.requester_longitude,
                request.search_radius,
                request.blood_type_needed
            )
            
            # Notify donors
            notifications_sent = 0
            for donor_info in nearby_donors[:20]:  # Notify top 20
                donor = DonorRepository.get_by_id(donor_info['id'])
                if donor and donor.user.email and donor.user.phone:
                    success = NotificationService.send_emergency_alert(
                        donor,
                        request,
                        donor_info['distance_km']
                    )
                    if success:
                        notifications_sent += 1
                        
                        # Update request
                        BloodRequestRepository.increment_notified(request)
            
            logger.info(
                f"Emergency alerts sent for request {request_id}: "
                f"{notifications_sent} donors notified"
            )
            
        except Exception as e:
            logger.error(f"Error processing emergency alerts: {str(e)}")

def process_emergency_alerts(request_id):
    """Process emergency alerts (synchronous wrapper)"""
    from flask import current_app
    
    app = current_app._get_current_object()
    
    # Start thread
    thread = threading.Thread(
        target=process_emergency_alerts_async,
        args=(app, request_id)
    )
    thread.daemon = True
    thread.start()
    
    return True

def notify_nearby_donors_async(app, request_id, donor_ids):
    """Notify specific donors about emergency"""
    with app.app_context():
        try:
            request = BloodRequestRepository.get_by_id(request_id)
            if not request:
                return
            
            for donor_id in donor_ids:
                donor = DonorRepository.get_by_id(donor_id)
                if donor:
                    # Calculate distance
                    distance = GeoService.geodesic_distance(
                        request.requester_latitude,
                        request.requester_longitude,
                        donor.latitude,
                        donor.longitude
                    )
                    
                    # Send notification
                    NotificationService.send_emergency_alert(donor, request, distance)
                    
                    # Update request
                    BloodRequestRepository.increment_notified(request)
                    
            logger.info(f"Notified {len(donor_ids)} donors for request {request_id}")
            
        except Exception as e:
            logger.error(f"Error notifying donors: {str(e)}")

def notify_nearby_donors(request_id, donor_ids):
    """Notify nearby donors"""
    from flask import current_app
    
    app = current_app._get_current_object()
    
    thread = threading.Thread(
        target=notify_nearby_donors_async,
        args=(app, request_id, donor_ids)
    )
    thread.daemon = True
    thread.start()
    
    return True

def escalate_emergency_if_needed(request_id):
    """Escalate emergency if no donors respond"""
    try:
        request = BloodRequestRepository.get_by_id(request_id)
        if not request:
            return
        
        # Check if emergency and no donors accepted after 30 minutes
        if (request.urgency == 'emergency' and 
            request.accepted_donors == 0 and
            request.created_at):
            
            from datetime import datetime, timedelta
            time_elapsed = datetime.utcnow() - request.created_at
            
            if time_elapsed > timedelta(minutes=30):
                # Escalate - notify admins
                from app.repositories.user_repo import UserRepository
                admins = UserRepository.get_all_admins()
                
                for admin in admins:
                    NotificationService.send_admin_alert(
                        admin,
                        request,
                        "No donors responded to emergency request"
                    )
                
                logger.warning(f"Emergency escalated for request {request_id}")
                
    except Exception as e:
        logger.error(f"Error escalating emergency: {str(e)}")

def send_bulk_sms_alerts(phone_numbers, message):
    """Send bulk SMS alerts"""
    try:
        success_count = 0
        for phone in phone_numbers:
            try:
                NotificationService.send_sms(phone, message)
                success_count += 1
            except Exception as e:
                logger.error(f"Failed to send SMS to {phone}: {str(e)}")
        
        logger.info(f"Bulk SMS sent: {success_count}/{len(phone_numbers)} successful")
        return success_count
        
    except Exception as e:
        logger.error(f"Error sending bulk SMS: {str(e)}")
        return 0