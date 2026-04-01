"""
Hospital API - API endpoints for hospital operations
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.hospital import Hospital
from app.models.blood_request import BloodRequest
from app.services.geo_service import GeoService
from app.repositories.hospital_repo import HospitalRepository
from app.utils.logger import logger

hospital_api_bp = Blueprint('hospital_api', __name__, url_prefix='/api/hospitals')

@hospital_api_bp.route('/nearby', methods=['GET'])
def nearby_hospitals():
    """Get nearby hospitals based on location"""
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
        logger.error(f"Error in nearby_hospitals API: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 400

@hospital_api_bp.route('/<int:hospital_id>', methods=['GET'])
def get_hospital(hospital_id):
    """Get hospital details by ID"""
    try:
        hospital = HospitalRepository.get_by_id(hospital_id)
        if not hospital:
            return jsonify({'status': 'error', 'message': 'Hospital not found'}), 404
        
        return jsonify({
            'status': 'success',
            'hospital': hospital.to_dict()
        })
    except Exception as e:
        logger.error(f"Error in get_hospital API: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 400

@hospital_api_bp.route('/', methods=['POST'])
@login_required
def create_hospital():
    """Create new hospital (admin only)"""
    try:
        if not current_user.is_admin():
            return jsonify({'status': 'error', 'message': 'Admin privileges required'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        required = ['name', 'phone', 'address', 'city', 'state', 'pincode', 'latitude', 'longitude']
        for field in required:
            if field not in data:
                return jsonify({'status': 'error', 'message': f'{field} is required'}), 400
        
        hospital = HospitalRepository.create(data)
        
        return jsonify({
            'status': 'success',
            'message': 'Hospital created successfully',
            'hospital': hospital.to_dict()
        }), 201
    except Exception as e:
        logger.error(f"Error in create_hospital API: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 400

@hospital_api_bp.route('/<int:hospital_id>', methods=['PUT'])
@login_required
def update_hospital(hospital_id):
    """Update hospital details (admin only)"""
    try:
        if not current_user.is_admin():
            return jsonify({'status': 'error', 'message': 'Admin privileges required'}), 403
        
        hospital = HospitalRepository.get_by_id(hospital_id)
        if not hospital:
            return jsonify({'status': 'error', 'message': 'Hospital not found'}), 404
        
        data = request.get_json()
        hospital = HospitalRepository.update(hospital, data)
        
        return jsonify({
            'status': 'success',
            'message': 'Hospital updated successfully',
            'hospital': hospital.to_dict()
        })
    except Exception as e:
        logger.error(f"Error in update_hospital API: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 400

@hospital_api_bp.route('/<int:hospital_id>/verify', methods=['POST'])
@login_required
def verify_hospital(hospital_id):
    """Verify hospital (admin only)"""
    try:
        if not current_user.is_admin():
            return jsonify({'status': 'error', 'message': 'Admin privileges required'}), 403
        
        hospital = HospitalRepository.get_by_id(hospital_id)
        if not hospital:
            return jsonify({'status': 'error', 'message': 'Hospital not found'}), 404
        
        hospital = HospitalRepository.verify(hospital)
        
        return jsonify({
            'status': 'success',
            'message': 'Hospital verified successfully'
        })
    except Exception as e:
        logger.error(f"Error in verify_hospital API: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 400

@hospital_api_bp.route('/<int:hospital_id>/requests', methods=['GET'])
def hospital_requests(hospital_id):
    """Get blood requests for a hospital"""
    try:
        requests = BloodRequest.query.filter_by(hospital_id=hospital_id)\
                                   .order_by(BloodRequest.created_at.desc())\
                                   .all()
        
        return jsonify({
            'status': 'success',
            'count': len(requests),
            'requests': [r.to_dict() for r in requests]
        })
    except Exception as e:
        logger.error(f"Error in hospital_requests API: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 400

@hospital_api_bp.route('/search', methods=['GET'])
def search_hospitals():
    """Search hospitals by criteria"""
    try:
        query = request.args.get('q', '')
        city = request.args.get('city')
        verified_only = request.args.get('verified_only', 'true').lower() == 'true'
        has_blood_bank = request.args.get('has_blood_bank', 'false').lower() == 'true'
        
        hospitals = HospitalRepository.search(
            query=query,
            city=city,
            verified_only=verified_only,
            has_blood_bank=has_blood_bank
        )
        
        return jsonify({
            'status': 'success',
            'count': len(hospitals),
            'hospitals': [h.to_dict() for h in hospitals]
        })
    except Exception as e:
        logger.error(f"Error in search_hospitals API: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 400

@hospital_api_bp.route('/stats', methods=['GET'])
def hospital_stats():
    """Get hospital statistics"""
    try:
        stats = {
            'total': HospitalRepository.count(),
            'verified': HospitalRepository.count_verified(),
            'with_blood_bank': Hospital.query.filter_by(has_blood_bank=True).count(),
            'by_city': HospitalRepository.count_by_city(limit=10)
        }
        
        return jsonify({
            'status': 'success',
            'stats': stats
        })
    except Exception as e:
        logger.error(f"Error in hospital_stats API: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 400