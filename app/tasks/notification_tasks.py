"""
Notification Tasks - Scheduled notification jobs
"""

from datetime import datetime, timedelta
from flask import current_app
from app.repositories.donor_repo import DonorRepository
from app.repositories.request_repo import BloodRequestRepository
from app.repositories.donation_repo import DonationRepository
from app.services.notification_service import NotificationService
from app.tasks.email_tasks import send_email
from app.utils.logger import logger

def send_reminders():
    """Send periodic reminders to donors"""
    try:
        # Get all donors
        donors = DonorRepository.get_all_donors()
        
        reminders_sent = 0
        for donor in donors:
            # Check if reminder needed
            if donor.last_donation_date:
                next_date = donor.last_donation_date + timedelta(days=90)
                days_until = (next_date - datetime.now()).days
                
                # Send reminder 7 days before eligibility
                if 0 < days_until <= 7:
                    NotificationService.send_donation_reminder(donor)
                    reminders_sent += 1
        
        logger.info(f"Sent {reminders_sent} donation reminders")
        return reminders_sent
        
    except Exception as e:
        logger.error(f"Error sending reminders: {str(e)}")
        return 0

def send_daily_summary():
    """Send daily summary to admins"""
    try:
        from app.repositories.user_repo import UserRepository
        
        # Get stats
        total_donors = DonorRepository.count()
        eligible_donors = DonorRepository.count_eligible()
        pending_requests = BloodRequestRepository.count_pending()
        emergency_requests = BloodRequestRepository.count_emergency()
        
        # Get admins
        admins = UserRepository.get_all_admins()
        
        summary_data = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'total_donors': total_donors,
            'eligible_donors': eligible_donors,
            'pending_requests': pending_requests,
            'emergency_requests': emergency_requests,
            'new_donors_today': DonorRepository.count_new_today(),
            'new_requests_today': BloodRequestRepository.count_new_today()
        }
        
        # Send to each admin
        for admin in admins:
            send_email(
                to_email=admin.email,
                subject=f"Daily Summary - {summary_data['date']}",
                template="daily_summary",
                **summary_data
            )
        
        logger.info(f"Daily summary sent to {len(admins)} admins")
        return len(admins)
        
    except Exception as e:
        logger.error(f"Error sending daily summary: {str(e)}")
        return 0

def send_weekly_report():
    """Send weekly report to admins"""
    try:
        from app.repositories.user_repo import UserRepository
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        # Get weekly stats
        new_donors = DonorRepository.count_new_in_range(start_date, end_date)
        new_requests = BloodRequestRepository.count_new_in_range(start_date, end_date)
        fulfilled_requests = BloodRequestRepository.count_fulfilled_in_range(start_date, end_date)
        
        # Get blood type distribution
        blood_type_stats = DonorRepository.count_by_blood_type()
        
        # Get top donors
        top_donors = DonorRepository.get_top_donors(limit=10)
        
        report_data = {
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'new_donors': new_donors,
            'new_requests': new_requests,
            'fulfilled_requests': fulfilled_requests,
            'blood_type_stats': blood_type_stats,
            'top_donors': top_donors,
            'total_donors': DonorRepository.count(),
            'total_requests': BloodRequestRepository.count()
        }
        
        # Get admins
        admins = UserRepository.get_all_admins()
        
        for admin in admins:
            send_email(
                to_email=admin.email,
                subject=f"Weekly Report - Week {datetime.now().isocalendar()[1]}",
                template="weekly_report",
                **report_data
            )
        
        logger.info(f"Weekly report sent to {len(admins)} admins")
        return len(admins)
        
    except Exception as e:
        logger.error(f"Error sending weekly report: {str(e)}")
        return 0

def send_request_updates():
    """Send updates about pending requests"""
    try:
        # Get pending requests older than 24 hours
        cutoff = datetime.now() - timedelta(hours=24)
        old_requests = BloodRequestRepository.get_pending_since(cutoff)
        
        updates_sent = 0
        for request in old_requests:
            # Notify requester
            if request.requester_email:
                send_email(
                    to_email=request.requester_email,
                    subject=f"Update on Blood Request {request.request_id}",
                    template="request_update",
                    request=request,
                    status="still pending"
                )
                updates_sent += 1
            
            # Update request
            request.updated_at = datetime.now()
        
        logger.info(f"Sent {updates_sent} request updates")
        return updates_sent
        
    except Exception as e:
        logger.error(f"Error sending request updates: {str(e)}")
        return 0

def send_thank_you_to_donors():
    """Send thank you messages to recent donors"""
    try:
        # Get donors who donated in last 24 hours
        cutoff = datetime.now() - timedelta(hours=24)
        recent_donations = DonationRepository.get_since(cutoff)
        
        thank_yous_sent = 0
        for donation in recent_donations:
            send_email(
                to_email=donation.donor.email,
                subject="Thank You for Saving Lives!",
                template="thank_you",
                donation=donation
            )
            thank_yous_sent += 1
        
        logger.info(f"Sent {thank_yous_sent} thank you messages")
        return thank_yous_sent
        
    except Exception as e:
        logger.error(f"Error sending thank you messages: {str(e)}")
        return 0