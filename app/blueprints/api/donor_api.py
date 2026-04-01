"""
Donor API - API endpoints for donor operations
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.donor import Donor
from app.models.donation import Donation
from app.models.blood_request import BloodRequest
from app.services.geo_service import GeoService
from app.services.eligibility_service import EligibilityService
from app.services.ml_service import MLService
from app.repositories.donor_repo import DonorRepository
from app.validators.donor_validator import DonorValidator
from app.utils.logger import logger
from datetime import datetime

donor_api_bp = Blueprint('donor_api', __name__, url_prefix='/api/donors')

@donor_api_bp.route('/nearby', methods=['GET'])
def nearby_donors():
    """Get nearby donors based on location"""
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
        logger.error(f"Error in nearby_donors API: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 400

@donor_api_bp.route('/<int:donor_id>', methods=['GET'])
def get_donor(donor_id):
    """Get donor details by ID"""
    try:
        donor = DonorRepository.get_by_id(donor_id)
        if not donor:
            return jsonify({'status': 'error', 'message': 'Donor not found'}), 404
        
        return jsonify({
            'status': 'success',
            'donor': donor.to_dict()
        })
    except Exception as e:
        logger.error(f"Error in get_donor API: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 400

@donor_api_bp.route('/<int:donor_id>/availability', methods=['GET'])
def check_availability(donor_id):
    """Check donor availability"""
    try:
        donor = DonorRepository.get_by_id(donor_id)
        if not donor:
            return jsonify({'status': 'error', 'message': 'Donor not found'}), 404
        
        eligibility = EligibilityService.get_eligibility_summary(donor)
        
        return jsonify({
            'status': 'success',
            'is_available': donor.is_available,
            'is_eligible': donor.is_eligible,
            'eligibility': eligibility
        })
    except Exception as e:
        logger.error(f"Error in check_availability API: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 400

@donor_api_bp.route('/<int:donor_id>/donations', methods=['GET'])
def get_donor_donations(donor_id):
    """Get donor's donation history"""
    try:
        donations = Donation.query.filter_by(donor_id=donor_id)\
                                 .order_by(Donation.donation_date.desc())\
                                 .all()
        
        return jsonify({
            'status': 'success',
            'count': len(donations),
            'donations': [d.to_dict() for d in donations]
        })
    except Exception as e:
        logger.error(f"Error in get_donor_donations API: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 400

@donor_api_bp.route('/<int:donor_id>/predict', methods=['GET'])
def predict_availability(donor_id):
    """Predict donor availability using ML"""
    try:
        donor = DonorRepository.get_by_id(donor_id)
        if not donor:
            return jsonify({'status': 'error', 'message': 'Donor not found'}), 404
        
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
            'prediction': prediction
        })
    except Exception as e:
        logger.error(f"Error in predict_availability API: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 400

@donor_api_bp.route('/<int:donor_id>/location', methods=['PUT'])
@login_required
def update_location(donor_id):
    """Update donor location"""
    try:
        if current_user.id != donor_id and not current_user.is_admin():
            return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
        
        data = request.get_json()
        lat = data.get('latitude')
        lon = data.get('longitude')
        
        if not lat or not lon:
            return jsonify({'status': 'error', 'message': 'Latitude and longitude required'}), 400
        
        donor = DonorRepository.get_by_user_id(donor_id)
        if not donor:
            return jsonify({'status': 'error', 'message': 'Donor not found'}), 404
        
        donor = DonorRepository.update_location(donor, lat, lon)
        
        return jsonify({
            'status': 'success',
            'message': 'Location updated successfully',
            'location': {'lat': donor.latitude, 'lon': donor.longitude}
        })
    except Exception as e:
        logger.error(f"Error in update_location API: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 400

@donor_api_bp.route('/search', methods=['GET'])
def search_donors():
    """Search donors by criteria"""
    try:
        query = request.args.get('q', '')
        blood_type = request.args.get('blood_type')
        city = request.args.get('city')
        available_only = request.args.get('available_only', 'false').lower() == 'true'
        
        donors = DonorRepository.search(
            query=query,
            blood_type=blood_type,
            city=city,
            available_only=available_only
        )
        
        return jsonify({
            'status': 'success',
            'count': len(donors),
            'donors': [d.to_dict() for d in donors]
        })
    except Exception as e:
        logger.error(f"Error in search_donors API: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 400

@donor_api_bp.route('/<int:donor_id>/status', methods=['PUT'])
@login_required
def update_status(donor_id):
    """Update donor availability status"""
    try:
        if current_user.id != donor_id and not current_user.is_admin():
            return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
        
        data = request.get_json()
        is_available = data.get('is_available')
        
        if is_available is None:
            return jsonify({'status': 'error', 'message': 'is_available field required'}), 400
        
        donor = DonorRepository.get_by_user_id(donor_id)
        if not donor:
            return jsonify({'status': 'error', 'message': 'Donor not found'}), 404
        
        donor = DonorRepository.update_availability(donor, is_available)
        
        return jsonify({
            'status': 'success',
            'message': f"Donor marked as {'available' if is_available else 'unavailable'}"
        })
    except Exception as e:
        logger.error(f"Error in update_status API: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 400

@donor_api_bp.route('/stats', methods=['GET'])
def donor_stats():
    """Get donor statistics"""
    try:
        stats = {
            'total': DonorRepository.count(),
            'eligible': DonorRepository.count_eligible(),
            'by_blood_type': DonorRepository.count_by_blood_type(),
            'by_city': DonorRepository.count_by_city(limit=10),
            'recent': len(DonorRepository.get_recent_donors(limit=10))
        }
        
        return jsonify({
            'status': 'success',
            'stats': stats
        })
    except Exception as e:
        logger.error(f"Error in donor_stats API: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 400