"""
Matching Service - Match donors with blood requests
"""

from app.services.geo_service import GeoService
from app.services.notification_service import NotificationService
from app.repositories.donor_repo import DonorRepository
from app.repositories.request_repo import BloodRequestRepository
from app.utils.logger import logger
from datetime import datetime

class MatchingService:
    """Service for matching donors with blood requests"""
    
    @staticmethod
    def find_matching_donors(blood_request, max_donors=20):
        """Find matching donors for a blood request"""
        try:
            # Get eligible donors with matching blood type
            donors = DonorRepository.get_eligible_donors_by_blood_type(
                blood_request.blood_type_needed
            )
            
            if not donors:
                logger.info(f"No matching donors found for request {blood_request.request_id}")
                return []
            
            # Calculate distances
            donors_with_distance = []
            for donor in donors:
                if donor.latitude and donor.longitude:
                    distance = GeoService.geodesic_distance(
                        blood_request.requester_latitude,
                        blood_request.requester_longitude,
                        donor.latitude,
                        donor.longitude
                    )
                    
                    if distance <= blood_request.search_radius:
                        donors_with_distance.append({
                            'donor': donor,
                            'distance': distance,
                            'score': MatchingService._calculate_match_score(donor, blood_request, distance)
                        })
            
            # Sort by match score (higher is better)
            donors_with_distance.sort(key=lambda x: x['score'], reverse=True)
            
            # Return top donors
            return donors_with_distance[:max_donors]
            
        except Exception as e:
            logger.error(f"Error finding matching donors: {str(e)}")
            return []
    
    @staticmethod
    def _calculate_match_score(donor, blood_request, distance):
        """Calculate match score for donor"""
        score = 100  # Base score
        
        # Distance factor (closer is better)
        max_distance = blood_request.search_radius
        distance_score = (1 - (distance / max_distance)) * 40
        score += distance_score
        
        # Donation history factor (regular donors get higher score)
        if donor.total_donations > 10:
            score += 20
        elif donor.total_donations > 5:
            score += 10
        elif donor.total_donations > 0:
            score += 5
        
        # Recency factor (recent donors might be more willing)
        if donor.last_donation_date:
            days_since = (datetime.now() - donor.last_donation_date).days
            if days_since < 90:
                score -= 30  # Recently donated, might want break
            elif days_since > 180:
                score += 10  # Haven't donated in a while
        
        # Availability factor
        if donor.is_available:
            score += 15
        
        return score
    
    @staticmethod
    def notify_matching_donors(blood_request):
        """Notify matching donors about blood request"""
        try:
            # Find matching donors
            matches = MatchingService.find_matching_donors(blood_request)
            
            if not matches:
                logger.info(f"No matching donors found for request {blood_request.request_id}")
                return 0
            
            # Notify donors
            notified_count = 0
            for match in matches[:10]:  # Notify top 10 donors
                donor = match['donor']
                
                # Send notification
                success = NotificationService.send_emergency_alert(
                    donor,
                    blood_request,
                    match['distance']
                )
                
                if success:
                    notified_count += 1
                    
                    # Update request
                    BloodRequestRepository.increment_notified(blood_request)
                    
                    # Log notification
                    logger.info(f"Notified donor {donor.user.id} for request {blood_request.request_id}")
            
            return notified_count
            
        except Exception as e:
            logger.error(f"Error notifying matching donors: {str(e)}")
            return 0
    
    @staticmethod
    def get_match_summary(blood_request):
        """Get summary of matching donors"""
        try:
            matches = MatchingService.find_matching_donors(blood_request)
            
            summary = {
                'total_matches': len(matches),
                'within_5km': len([m for m in matches if m['distance'] <= 5]),
                'within_10km': len([m for m in matches if m['distance'] <= 10]),
                'average_distance': sum(m['distance'] for m in matches) / len(matches) if matches else 0,
                'top_matches': [
                    {
                        'donor_id': m['donor'].id,
                        'name': m['donor'].user.name,
                        'blood_type': m['donor'].blood_type,
                        'distance': round(m['distance'], 2),
                        'score': round(m['score'], 2)
                    }
                    for m in matches[:5]
                ]
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting match summary: {str(e)}")
            return {}
    
    @staticmethod
    def auto_match_emergency_requests():
        """Automatically match pending emergency requests"""
        try:
            from app.models.blood_request import BloodRequest
            
            # Get pending emergency requests
            emergency_requests = BloodRequest.query.filter_by(
                urgency='emergency',
                status='pending'
            ).all()
            
            matched_count = 0
            for request in emergency_requests:
                # Check if already notified
                if request.notified_donors == 0:
                    notified = MatchingService.notify_matching_donors(request)
                    if notified > 0:
                        matched_count += 1
            
            logger.info(f"Auto-matched {matched_count} emergency requests")
            return matched_count
            
        except Exception as e:
            logger.error(f"Error auto-matching emergency requests: {str(e)}")
            return 0
        