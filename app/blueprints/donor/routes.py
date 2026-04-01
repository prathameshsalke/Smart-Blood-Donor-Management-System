"""
Donor Blueprint - Donor dashboard and features
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, send_file, current_app
from flask_login import login_required, current_user
from app import db
from app.models.donor import Donor
from app.models.donation import Donation
from app.models.blood_request import BloodRequest
from app.services.geo_service import GeoService
from app.services.eligibility_service import EligibilityService
from app.services.certificate_service import CertificateService
from app.services.ml_service import MLService
from app.models.user import User
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import json
import os

donor_bp = Blueprint('donor', __name__, template_folder='templates')

# Configuration for file uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_upload_folder():
    """Get or create upload folder path"""
    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'profiles')
    os.makedirs(upload_folder, exist_ok=True)
    return upload_folder

@donor_bp.route('/dashboard')
@login_required
def dashboard():
    """Donor dashboard"""
    if not current_user.is_donor():
        flash('Access denied. Donor privileges required.', 'danger')
        return redirect(url_for('index'))
    
    donor = current_user.donor_profile
    
    # Get statistics
    total_donations = Donation.query.filter_by(donor_id=current_user.id).count()
    recent_donations = Donation.query.filter_by(donor_id=current_user.id)\
                           .order_by(Donation.donation_date.desc()).limit(5).all()
    
    # Check eligibility
    eligibility = EligibilityService.get_eligibility_summary(donor)
    
    # Get nearby requests
    if donor and donor.latitude and donor.longitude:
        nearby_requests = BloodRequest.query.filter_by(
            blood_type_needed=donor.blood_type,
            status='pending'
        ).limit(5).all()
    else:
        nearby_requests = []
    
    # Pass current year to template for footer
    current_year = datetime.now().year
    
    return render_template('donor/dashboard.html',
                         donor=donor,
                         total_donations=total_donations,
                         recent_donations=recent_donations,
                         eligibility=eligibility,
                         nearby_requests=nearby_requests,
                         current_year=current_year,
                         now=datetime.now,
                         timedelta=timedelta,
                         title='Donor Dashboard')

@donor_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit donor profile"""
    donor = current_user.donor_profile
    
    if request.method == 'POST':
        # Update fields
        donor.address = request.form.get('address')
        donor.city = request.form.get('city')
        donor.state = request.form.get('state')
        donor.pincode = request.form.get('pincode')
        donor.emergency_contact_name = request.form.get('emergency_contact_name')
        donor.emergency_contact_phone = request.form.get('emergency_contact_phone')
        donor.emergency_contact_relation = request.form.get('emergency_contact_relation')
        donor.medical_conditions = request.form.get('medical_conditions')
        donor.medications = request.form.get('medications')
        
        # Update nationality and disability
        donor.nationality = request.form.get('nationality', 'Indian')
        donor.has_disability = request.form.get('has_disability') == 'on'
        donor.disability = request.form.get('disability') if donor.has_disability else None
        
        # Update location if provided
        lat = request.form.get('latitude')
        lon = request.form.get('longitude')
        if lat and lon:
            donor.latitude = float(lat)
            donor.longitude = float(lon)
            donor.location_updated_at = datetime.utcnow()
        
        # Update availability
        donor.is_available = request.form.get('is_available') == 'on'
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('donor.dashboard'))
    
    return render_template('donor/edit_profile.html', 
                         donor=donor,
                         current_year=datetime.now().year,
                         title='Edit Profile')

@donor_bp.route('/update-profile-photo', methods=['POST'])
@login_required
def update_profile_photo():
    """Update donor profile photo via AJAX - Uses donor_unique_id for filename"""
    try:
        # Check if file exists in request
        if 'photo' not in request.files:
            return jsonify({
                'status': 'error', 
                'message': 'No file uploaded'
            }), 400
        
        file = request.files['photo']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({
                'status': 'error', 
                'message': 'No file selected'
            }), 400
        
        # Validate file type
        if not allowed_file(file.filename):
            return jsonify({
                'status': 'error', 
                'message': 'Invalid file type. Allowed: PNG, JPG, JPEG, GIF'
            }), 400
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({
                'status': 'error', 
                'message': f'File too large. Maximum size is {MAX_FILE_SIZE//(1024*1024)}MB'
            }), 400
        
        # Get donor and their unique ID
        donor = current_user.donor_profile
        donor_unique_id = donor.donor_unique_id  # Get the unique donor ID
        
        # Get upload folder
        upload_folder = get_upload_folder()
        
        # Generate filename using donor_unique_id
        filename = secure_filename(file.filename)
        ext = filename.rsplit('.', 1)[1].lower()
        # Format: donor_DNR2402191530A7B9_20250219153045.jpg
        new_filename = f"donor_{donor_unique_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{ext}"
        filepath = os.path.join(upload_folder, new_filename)
        
        # Save file
        file.save(filepath)
        
        # Delete old photo if exists
        if donor.profile_photo:
            old_filepath = os.path.join(current_app.root_path, 'static', 'uploads', 'profiles', donor.profile_photo)
            if os.path.exists(old_filepath):
                try:
                    os.remove(old_filepath)
                except:
                    pass  # Ignore errors if file doesn't exist
        
        # Update donor profile with new filename
        donor.profile_photo = new_filename
        db.session.commit()
        
        # Generate URL for the photo response
        photo_url = url_for('static', filename=f"uploads/profiles/{new_filename}", _external=True)
        
        return jsonify({
            'status': 'success',
            'message': 'Photo uploaded successfully',
            'photo_url': photo_url
        })
        
    except Exception as e:
        print(f"Error uploading photo: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Server error: {str(e)}'
        }), 500

@donor_bp.route('/save-camera-photo', methods=['POST'])
@login_required
def save_camera_photo():
    """Save photo captured from camera - Uses donor_unique_id for filename"""
    try:
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({'status': 'error', 'message': 'No image data'}), 400
        
        image_data = data['image']
        
        # Remove data URL prefix if present
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        # Decode base64
        import base64
        import uuid
        from PIL import Image
        import io
        
        image_bytes = base64.b64decode(image_data)
        
        # Get donor and their unique ID
        donor = current_user.donor_profile
        donor_unique_id = donor.donor_unique_id
        
        # Generate filename using donor_unique_id
        upload_folder = get_upload_folder()
        # Format: donor_DNR2402191530A7B9_camera_20250219153045.jpg
        new_filename = f"donor_{donor_unique_id}_camera_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
        filepath = os.path.join(upload_folder, new_filename)
        
        # Save and optimize image
        img = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB if necessary
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        
        # Resize if too large (max 800x800)
        if img.size[0] > 800 or img.size[1] > 800:
            img.thumbnail((800, 800), Image.Resampling.LANCZOS)
        
        # Save with optimization
        img.save(filepath, 'JPEG', quality=85, optimize=True)
        
        # Delete old photo if exists
        if donor.profile_photo:
            old_filepath = os.path.join(current_app.root_path, 'static', 'uploads', 'profiles', donor.profile_photo)
            if os.path.exists(old_filepath):
                try:
                    os.remove(old_filepath)
                except:
                    pass
        
        # Update donor profile
        donor.profile_photo = new_filename
        db.session.commit()
        
        photo_url = url_for('static', filename=f"uploads/profiles/{new_filename}", _external=True)
        
        return jsonify({
            'status': 'success',
            'message': 'Photo saved successfully',
            'photo_url': photo_url
        })
        
    except Exception as e:
        print(f"Camera save error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@donor_bp.route('/camera-capture')
@login_required
def camera_capture():
    """Camera capture page for taking profile photos"""
    return render_template('donor/camera_capture.html',
                         current_year=datetime.now().year,
                         title='Take Photo')

@donor_bp.route('/remove-profile-photo', methods=['POST'])
@login_required
def remove_profile_photo():
    """Remove donor profile photo"""
    try:
        donor = current_user.donor_profile
        
        # Delete the photo file if it exists
        if donor.profile_photo:
            filepath = os.path.join(current_app.root_path, 'static', 'uploads', 'profiles', donor.profile_photo)
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except Exception as e:
                    print(f"Error deleting file: {e}")
        
        # Remove photo path from database
        donor.profile_photo = None
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Profile photo removed successfully'
        })
        
    except Exception as e:
        print(f"Error removing photo: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@donor_bp.route('/donation-history')
@login_required
def donation_history():
    """View donation history"""
    donations = Donation.query.filter_by(donor_id=current_user.id)\
                    .order_by(Donation.donation_date.desc()).all()
    
    return render_template('donor/donation_history.html', 
                         donations=donations,
                         current_year=datetime.now().year,
                         now=datetime.now,
                         title='Donation History')

@donor_bp.route('/eligibility-status')
@login_required
def eligibility_status():
    """Check eligibility status"""
    donor = current_user.donor_profile
    eligibility = EligibilityService.get_eligibility_summary(donor)
    
    return render_template('donor/eligibility_status.html',
                         donor=donor,
                         eligibility=eligibility,
                         current_year=datetime.now().year,
                         now=datetime.now,
                         timedelta=timedelta,
                         title='Eligibility Status')

@donor_bp.route('/nearby-donors')
@login_required
def nearby_donors():
    """Find nearby donors - shows all donors sorted by distance"""
    donor = current_user.donor_profile
    
    # Check if donor has location
    if not donor or not donor.latitude or not donor.longitude:
        flash('Please update your location first to find nearby donors', 'warning')
        return redirect(url_for('donor.edit_profile'))
    
    # Get parameters with defaults
    try:
        radius = request.args.get('radius', 50, type=int)  # Increased default radius
        if radius < 1 or radius > 500:  # Increased max radius
            radius = 50
    except (TypeError, ValueError):
        radius = 50
    
    blood_type = request.args.get('blood_type')
    if blood_type not in ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-', None]:
        blood_type = None
    
    # Find nearby donors - use include_all=True to get all donors sorted by distance
    try:
        # Get all donors with distance (include_all=True)
        all_donors = GeoService.find_nearby_donors(
            donor.latitude, 
            donor.longitude, 
            radius,
            blood_type,
            include_all=True  # This returns all donors sorted by distance
        )
        
        # Get only nearby donors within radius
        nearby_donors = GeoService.find_nearby_donors(
            donor.latitude, 
            donor.longitude, 
            radius,
            blood_type,
            include_all=False
        )
        
        current_year = datetime.now().year
        
        return render_template('donor/nearby_donors.html',
                             donors=all_donors,  # Pass all donors sorted by distance
                             nearby_donors=nearby_donors,  # Pass nearby donors separately
                             total_donors=len(all_donors),
                             nearby_count=len(nearby_donors),
                             radius=radius,
                             blood_type=blood_type,
                             current_year=current_year,
                             user_lat=donor.latitude,
                             user_lon=donor.longitude,
                             title='Nearby Donors')
    except Exception as e:
        print(f"Error finding nearby donors: {e}")
        flash('Error finding nearby donors. Please try again.', 'danger')
        return redirect(url_for('donor.dashboard'))

@donor_bp.route('/find-donors')
@login_required
def find_donors():
    """Find donors search page - shows all donors with filtering"""
    donor = current_user.donor_profile
    
    # Get search parameters
    city = request.args.get('city', '')
    blood_type = request.args.get('blood_type', '')
    sort_by = request.args.get('sort_by', 'distance')  # distance, name, blood_type
    
    # Base query
    query = Donor.query.join(User).filter(User.is_active == True)
    
    # Apply filters
    if city:
        query = query.filter(Donor.city.ilike(f'%{city}%'))
    
    if blood_type:
        query = query.filter(Donor.blood_type == blood_type)
    
    # Get all donors
    all_donors = query.all()
    
    # Calculate distance for each donor if user has location
    donors_with_distance = []
    if donor and donor.latitude and donor.longitude:
        for d in all_donors:
            if d.latitude and d.longitude:
                distance = GeoService.geodesic_distance(
                    donor.latitude, donor.longitude,
                    d.latitude, d.longitude
                )
                donor_dict = d.to_dict()
                donor_dict['distance_km'] = distance
                donors_with_distance.append(donor_dict)
            else:
                donor_dict = d.to_dict()
                donor_dict['distance_km'] = None
                donors_with_distance.append(donor_dict)
        
        # Sort by distance
        donors_with_distance.sort(key=lambda x: x['distance_km'] if x['distance_km'] is not None else float('inf'))
    else:
        donors_with_distance = [d.to_dict() for d in all_donors]
        if sort_by == 'name':
            donors_with_distance.sort(key=lambda x: x['name'])
        elif sort_by == 'blood_type':
            donors_with_distance.sort(key=lambda x: x['blood_type'])
    
    current_year = datetime.now().year
    
    return render_template('donor/find_donors.html',
                         donors=donors_with_distance,
                         total_count=len(donors_with_distance),
                         search_city=city,
                         search_blood_type=blood_type,
                         sort_by=sort_by,
                         current_year=current_year,
                         user_lat=donor.latitude if donor else None,
                         user_lon=donor.longitude if donor else None,
                         title='Find Donors')

@donor_bp.route('/nearby-hospitals')
@login_required
def nearby_hospitals():
    """Find nearby hospitals"""
    donor = current_user.donor_profile
    
    if not donor or not donor.latitude or not donor.longitude:
        flash('Please update your location first', 'warning')
        return redirect(url_for('donor.edit_profile'))
    
    radius = request.args.get('radius', 20, type=int)
    
    nearby = GeoService.find_nearby_hospitals(
        donor.latitude, 
        donor.longitude, 
        radius
    )
    
    return render_template('donor/nearby_hospitals.html',
                         hospitals=nearby,
                         radius=radius,
                         current_year=datetime.now().year,
                         title='Nearby Hospitals')

@donor_bp.route('/emergency-search')
@login_required
def emergency_search():
    """Emergency donor search"""
    return render_template('donor/emergency_search.html',
                         current_year=datetime.now().year,
                         title='Emergency Search')

@donor_bp.route('/respond/<request_id>')
@login_required
def respond_to_request(request_id):
    """Respond to blood request"""
    blood_request = BloodRequest.query.filter_by(request_id=request_id).first_or_404()
    
    donor = current_user.donor_profile
    
    if blood_request.blood_type_needed != donor.blood_type:
        flash('Your blood type does not match this request', 'warning')
        return redirect(url_for('donor.dashboard'))
    
    existing = Donation.query.filter_by(
        donor_id=current_user.id,
        request_id=blood_request.id
    ).first()
    
    if existing:
        flash('You have already responded to this request', 'info')
    else:
        donation = Donation(
            donor_id=current_user.id,
            donor_name=current_user.name,
            donor_blood_type=donor.blood_type,
            request_id=blood_request.id,
            request_ref=blood_request.request_id
        )
        db.session.add(donation)
        blood_request.accepted_donors += 1
        db.session.commit()
        flash('Thank you for responding to the request!', 'success')
    
    return redirect(url_for('donor.dashboard'))

@donor_bp.route('/certificate/<donation_id>')
@login_required
def download_certificate(donation_id):
    """Download donation certificate"""
    donation = Donation.query.filter_by(
        donation_id=donation_id,
        donor_id=current_user.id
    ).first_or_404()
    
    if not donation.certificate_generated:
        # Generate certificate
        cert_service = CertificateService()
        cert_path = cert_service.generate_donation_certificate(donation)
        
        if cert_path:
            donation.certificate_generated = True
            donation.certificate_path = cert_path
            db.session.commit()
            
            # Certificate notification will be sent after 1 minute
            # by the scheduled task in CertificateService
            flash('Certificate generated! You will receive a notification shortly.', 'success')
    
    if donation.certificate_path and os.path.exists(donation.certificate_path):
        return send_file(
            donation.certificate_path,
            as_attachment=True,
            download_name=f"certificate_{donation.donation_id}.pdf",
            mimetype='application/pdf'
        )
    else:
        flash('Certificate not found', 'danger')
        return redirect(url_for('donor.donation_history'))

@donor_bp.route('/update-location', methods=['POST'])
@login_required
def update_location():
    """Update donor location via AJAX with comprehensive error handling"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'status': 'error', 
                'message': 'No data provided'
            }), 400
        
        lat = data.get('latitude')
        lon = data.get('longitude')
        accuracy = data.get('accuracy')
        force_update = data.get('force_update', False)
        auto_update_address = data.get('auto_update_address', True)
        
        # Validate required fields
        if lat is None or lon is None:
            return jsonify({
                'status': 'error', 
                'message': 'Latitude and longitude are required'
            }), 400
        
        try:
            lat = float(lat)
            lon = float(lon)
        except (TypeError, ValueError):
            return jsonify({
                'status': 'error', 
                'message': 'Invalid coordinate format'
            }), 400
        
        # Validate coordinate ranges
        if lat < -90 or lat > 90 or lon < -180 or lon > 180:
            return jsonify({
                'status': 'error', 
                'message': 'Coordinates out of valid range'
            }), 400
        
        donor = current_user.donor_profile
        if not donor:
            return jsonify({
                'status': 'error', 
                'message': 'Donor profile not found'
            }), 404
        
        # Calculate distance moved if previous location exists
        distance_moved = None
        if donor.latitude and donor.longitude:
            try:
                from geopy.distance import geodesic
                old_loc = (donor.latitude, donor.longitude)
                new_loc = (lat, lon)
                distance_moved = geodesic(old_loc, new_loc).meters
            except Exception as e:
                current_app.logger.warning(f"Distance calculation error: {e}")
        
        # Update donor location
        donor.latitude = lat
        donor.longitude = lon
        donor.location_updated_at = datetime.utcnow()
        
        # Reverse geocode to get address (if requested and accuracy is good enough)
        address_info = None
        if auto_update_address and (not accuracy or accuracy < 500):  # Only if accuracy < 500m
            try:
                address_info = GeoService.reverse_geocode(lat, lon)
                
                if address_info:
                    # Update address fields
                    if address_info.get('city'):
                        donor.city = address_info.get('city')
                    if address_info.get('state'):
                        donor.state = address_info.get('state')
                    if address_info.get('address') and (not donor.address or auto_update_address):
                        donor.address = address_info.get('address')
            except Exception as e:
                current_app.logger.error(f"Reverse geocoding error: {e}")
        
        db.session.commit()
        
        # Prepare success response
        response_data = {
            'status': 'success',
            'message': 'Location updated successfully',
            'accuracy': accuracy,
            'distance_moved': round(distance_moved, 1) if distance_moved is not None else None,
            'location': {
                'lat': donor.latitude,
                'lon': donor.longitude,
                'updated_at': donor.location_updated_at.isoformat() if donor.location_updated_at else None
            },
            'address': {
                'city': donor.city,
                'state': donor.state,
                'address': donor.address,
                'pincode': donor.pincode
            }
        }
        
        if address_info:
            response_data['reverse_geocode'] = address_info
        
        return jsonify(response_data), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Location update error: {str(e)}")
        return jsonify({
            'status': 'error', 
            'message': 'Server error occurred. Please try again.'
        }), 500

@donor_bp.route('/predict-availability')
@login_required
def predict_availability():
    """Get ML prediction for availability"""
    donor = current_user.donor_profile
    
    ml_service = MLService()
    
    # Calculate days since last donation
    days_since_last = 999
    if donor.last_donation_date:
        days_since_last = (datetime.now() - donor.last_donation_date).days
    
    # Prepare donor data
    donor_data = {
        'days_since_last': days_since_last,
        'gender': donor.gender,
        'total_donations': donor.total_donations,
        'weight': donor.weight,
        'age': donor.calculate_age(),
        'blood_type': donor.blood_type,
        'is_available': donor.is_available
    }
    
    prediction = ml_service.predict_donor_availability(donor_data)
    
    return render_template('donor/prediction.html',
                         prediction=prediction,
                         current_year=datetime.now().year,
                         title='Availability Prediction')

@donor_bp.route('/public/<int:donor_id>')
def public_profile(donor_id):
    """Public donor profile - no login required"""
    donor = Donor.query.get_or_404(donor_id)
    
    donations = Donation.query.filter_by(
        donor_id=donor.user_id,
        is_verified=True
    ).order_by(Donation.donation_date.desc()).limit(10).all()
    
    return render_template('donor/public_profile.html',
                         donor=donor,
                         donations=donations,
                         current_year=datetime.now().year,
                         title=f"{donor.user.name}'s Profile")

@donor_bp.route('/messages')
@login_required
def messages():
    """View all messages for donor"""
    page = request.args.get('page', 1, type=int)
    message_type = request.args.get('type', None)
    
    from app.services.message_service import MessageService
    
    messages_pagination = MessageService.get_messages(
        user_id=current_user.id,
        page=page,
        per_page=20,
        message_type=message_type
    )
    
    unread_count = MessageService.get_unread_count(current_user.id)
    
    return render_template('donor/messages.html',
                         messages=messages_pagination.items,
                         pagination=messages_pagination,
                         unread_count=unread_count,
                         current_type=message_type,
                         current_year=datetime.now().year,
                         title='Messages')

@donor_bp.route('/messages/<message_id>')
@login_required
def view_message(message_id):
    """View a single message"""
    from app.models.message import Message
    from app.services.message_service import MessageService
    
    message = Message.query.filter_by(
        message_id=message_id,
        recipient_id=current_user.id
    ).first_or_404()
    
    # Mark as read
    if not message.is_read:
        MessageService.mark_as_read(message_id, current_user.id)
    
    return render_template('donor/view_message.html',
                         message=message,
                         current_year=datetime.now().year,
                         title=message.subject)

@donor_bp.route('/messages/mark-read/<message_id>', methods=['POST'])
@login_required
def mark_message_read(message_id):
    """Mark a message as read via AJAX"""
    from app.services.message_service import MessageService
    
    success = MessageService.mark_as_read(message_id, current_user.id)
    
    return jsonify({
        'status': 'success' if success else 'error',
        'message': 'Message marked as read' if success else 'Failed to mark as read'
    })

@donor_bp.route('/messages/mark-all-read', methods=['POST'])
@login_required
def mark_all_read():
    """Mark all messages as read"""
    from app.services.message_service import MessageService
    
    MessageService.mark_all_as_read(current_user.id)
    
    return jsonify({
        'status': 'success',
        'message': 'All messages marked as read'
    })

@donor_bp.route('/messages/archive/<message_id>', methods=['POST'])
@login_required
def archive_message(message_id):
    """Archive a message"""
    from app.services.message_service import MessageService
    
    success = MessageService.archive_message(message_id, current_user.id)
    
    return jsonify({
        'status': 'success' if success else 'error',
        'message': 'Message archived' if success else 'Failed to archive'
    })

@donor_bp.route('/contact/<int:donor_id>', methods=['GET', 'POST'])
@login_required
def contact_donor(donor_id):
    """Contact another donor via message or phone"""
    target_donor = Donor.query.get_or_404(donor_id)
    
    if request.method == 'POST':
        message_type = request.form.get('message_type')
        message_content = request.form.get('message')
        
        if message_type == 'sms':
            # Send SMS (simulated for now)
            from app.services.notification_service import NotificationService
            success = NotificationService.send_sms(
                target_donor.user.phone,
                f"Message from {current_user.name}: {message_content}"
            )
            if success:
                flash('SMS sent successfully!', 'success')
            else:
                flash('Failed to send SMS. Please try again.', 'danger')
                
        elif message_type == 'email':
            # Send email
            from app.services.email_service import EmailService
            subject = f"Message from {current_user.name} - Blood Donor System"
            body = f"""
            Hello {target_donor.user.name},
            
            You have received a message from {current_user.name} ({current_user.email})
            
            Message:
            {message_content}
            
            Please respond to this email or contact them directly.
            
            - Smart Blood Donor System
            """
            success = EmailService.send_email(
                target_donor.user.email,
                subject,
                body
            )
            if success:
                flash('Email sent successfully!', 'success')
            else:
                flash('Failed to send email. Please try again.', 'danger')
        
        return redirect(url_for('donor.nearby_donors'))
    
    return render_template('donor/contact_donor.html',
                         donor=target_donor,
                         current_year=datetime.now().year,
                         title=f'Contact {target_donor.user.name}')

@donor_bp.route('/send-message', methods=['POST'])
@login_required
def send_message():
    """Send message to another donor (in-app)"""
    try:
        data = request.get_json()
        recipient_id = data.get('recipient_id')
        message_content = data.get('message')
        
        recipient = User.query.get(recipient_id)
        if not recipient:
            return jsonify({'status': 'error', 'message': 'Recipient not found'}), 404
        
        # Send in-app message
        from app.services.message_service import MessageService
        message = MessageService.send_message(
            recipient_id=recipient_id,
            subject=f"Message from {current_user.name}",
            content=message_content,
            message_type='contact',
            sender_id=current_user.id
        )
        
        # Send email notification
        from app.services.email_service import EmailService
        EmailService.send_notification(
            recipient.email,
            f"New message from {current_user.name} - Blood Donor System",
            f"""
            You have received a new message from {current_user.name}.
            
            Message:
            {message_content}
            
            Login to your dashboard to reply: {url_for('donor.messages', _external=True)}
            """
        )
        
        return jsonify({
            'status': 'success',
            'message': 'Message sent successfully',
            'message_id': message.message_id
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@donor_bp.route('/notifications/count')
@login_required
def notification_count():
    """Get unread notification count via AJAX"""
    from app.services.message_service import MessageService
    
    count = MessageService.get_unread_count(current_user.id)
    
    return jsonify({
        'count': count
    })