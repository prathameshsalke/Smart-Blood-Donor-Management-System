"""
API Blueprint - REST API endpoints
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.donor import Donor
from app.models.blood_request import BloodRequest
from app.models.hospital import Hospital
from app.models.donation import Donation
from app.services.geo_service import GeoService
from app.services.ml_service import MLService
from app.services.notification_service import NotificationService
from datetime import datetime
import json

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/donors/nearby', methods=['GET'])
def api_nearby_donors():
    """API endpoint to find nearby donors"""
    try:
        lat = float(request.args.get('lat'))
        lon = float(request.args.get('lon'))
        radius = int(request.args.get('radius', 10))
        blood_type = request.args.get('blood_type')
        
        donors = GeoService.find_nearby_donors(lat, lon, radius, blood_type)
        
        return jsonify({
            'status': 'success',
            'count': len(donors),
            'donors': donors
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@api_bp.route('/hospitals/nearby', methods=['GET'])
def api_nearby_hospitals():
    """API endpoint to find nearby hospitals"""
    try:
        lat = float(request.args.get('lat'))
        lon = float(request.args.get('lon'))
        radius = int(request.args.get('radius', 20))
        
        hospitals = GeoService.find_nearby_hospitals(lat, lon, radius)
        
        return jsonify({
            'status': 'success',
            'count': len(hospitals),
            'hospitals': hospitals
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@api_bp.route('/requests/emergency', methods=['POST'])
def api_emergency_request():
    """API endpoint for emergency blood requests"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required = ['patient_name', 'blood_type', 'requester_lat', 'requester_lon']
        if not all(field in data for field in required):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Create blood request
        blood_request = BloodRequest(
            requester_id=current_user.id if current_user.is_authenticated else None,
            requester_name=data.get('requester_name', 'Anonymous'),
            requester_phone=data.get('requester_phone', ''),
            requester_email=data.get('requester_email'),
            patient_name=data['patient_name'],
            blood_type_needed=data['blood_type'],
            units_needed=data.get('units_needed', 1),
            hospital_name=data.get('hospital_name'),
            urgency='emergency',
            requester_latitude=data['requester_lat'],
            requester_longitude=data['requester_lon'],
            search_radius=data.get('radius', 10)
        )
        
        db.session.add(blood_request)
        db.session.flush()
        
        # Find nearby donors
        nearby_donors = GeoService.find_nearby_donors(
            data['requester_lat'],
            data['requester_lon'],
            data.get('radius', 10),
            data['blood_type']
        )
        
        # Notify donors
        notifications_sent = 0
        for donor_info in nearby_donors[:20]:  # Notify top 20
            donor = Donor.query.get(donor_info['id'])
            if donor and donor.user.email:
                NotificationService.send_emergency_alert(
                    donor, 
                    blood_request, 
                    donor_info['distance_km']
                )
                notifications_sent += 1
        
        blood_request.notified_donors = notifications_sent
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'request_id': blood_request.request_id,
            'notified_donors': notifications_sent,
            'message': f'Emergency request created. {notifications_sent} donors notified.'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@api_bp.route('/donors/<int:donor_id>/availability', methods=['GET'])
def api_donor_availability(donor_id):
    """Get donor availability prediction"""
    try:
        donor = Donor.query.get_or_404(donor_id)
        
        ml_service = MLService()
        donor_data = {
            'age': donor.calculate_age(),
            'blood_type': donor.blood_type,
            'total_donations': donor.total_donations,
            'days_since_last': (datetime.now() - donor.last_donation_date).days if donor.last_donation_date else 999
        }
        
        prediction = ml_service.predict_donor_availability(donor_data)
        
        return jsonify({
            'status': 'success',
            'donor_id': donor_id,
            'prediction': prediction
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@api_bp.route('/forecast/demand', methods=['GET'])
def api_demand_forecast():
    """Get blood demand forecast"""
    try:
        blood_type = request.args.get('blood_type')
        months = int(request.args.get('months', 3))
        
        ml_service = MLService()
        forecast = ml_service.forecast_demand(blood_type, months)
        
        return jsonify({
            'status': 'success',
            'forecast': forecast
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@api_bp.route('/verify/certificate/<donation_id>', methods=['GET'])
def api_verify_certificate(donation_id):
    """Verify donation certificate"""
    from app.services.certificate_service import CertificateService
    
    cert_service = CertificateService()
    result = cert_service.verify_certificate(donation_id)
    
    return jsonify(result)

@api_bp.route('/stats', methods=['GET'])
def api_stats():
    """Get system statistics"""
    try:
        total_donors = Donor.query.count()
        eligible_donors = Donor.query.filter_by(is_eligible=True).count()
        total_requests = BloodRequest.query.count()
        pending_requests = BloodRequest.query.filter_by(status='pending').count()
        total_donations = Donation.query.count()
        
        # Donations by blood type
        blood_type_stats = {}
        for bt in ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']:
            count = Donation.query.filter_by(donor_blood_type=bt).count()
            blood_type_stats[bt] = count
        
        return jsonify({
            'status': 'success',
            'stats': {
                'total_donors': total_donors,
                'eligible_donors': eligible_donors,
                'total_requests': total_requests,
                'pending_requests': pending_requests,
                'total_donations': total_donations,
                'blood_type_distribution': blood_type_stats
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@api_bp.route('/health', methods=['GET'])
def api_health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })