# app/blueprints/api/emergency_api.py
from flask import Blueprint, request, jsonify
from app.services.geo_service import GeoService
from app.services.matching_service import MatchingService
from app.services.notification_service import NotificationService
from app.repositories.request_repo import BloodRequestRepository
from app.utils.logger import log_admin_activity # Example logging
from datetime import datetime

emergency_api_bp = Blueprint('emergency_api', __name__, url_prefix='/api/emergency')

@emergency_api_bp.route('/search', methods=['POST'])
def emergency_search():
    """API endpoint to handle an emergency blood request."""
    data = request.get_json()

    # Validate input
    required_fields = ['user_lat', 'user_lon', 'blood_type', 'patient_name', 'hospital_id']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    user_lat = data['user_lat']
    user_lon = data['user_lon']
    blood_type = data['blood_type']
    patient_name = data['patient_name']
    hospital_id = data['hospital_id']

    # 1. Find nearby donors using GeoService
    nearby_donors = GeoService.find_nearby_donors(user_lat, user_lon, radius_km=10)

    # 2. Filter donors by blood type
    matching_donors = [
        d for d in nearby_donors
        if d['donor'].blood_type == blood_type and d['donor'].is_eligible
    ]

    # 3. Create an emergency request in the database
    new_request = BloodRequestRepository.create_emergency_request(
        patient_name=patient_name,
        blood_type=blood_type,
        hospital_id=hospital_id,
        requester_lat=user_lat,
        requester_lon=user_lon
    )

    # 4. Trigger notifications to matching donors (async)
    for donor_info in matching_donors[:10]:  # Notify top 10 closest donors
        donor = donor_info['donor']
        distance = donor_info['distance_km']
        NotificationService.send_emergency_alert(donor, new_request, distance)
        # In a real app, you might want to log this action or update donor status

    # 5. Return the list of notified donors to the requester
    response_donors = [{
        'donor_id': d['donor'].id,
        'name': d['donor'].name,
        'distance_km': d['distance_km'],
        'phone': d['donor'].phone, # Be careful with PII
        'blood_type': d['donor'].blood_type
    } for d in matching_donors[:10]]

    log_admin_activity(f"Emergency request for {blood_type} created. {len(matching_donors)} potential donors notified.")

    return jsonify({
        'message': 'Emergency request processed successfully.',
        'request_id': new_request.id,
        'notified_donors_count': len(matching_donors[:10]),
        'donors': response_donors
    }), 201
