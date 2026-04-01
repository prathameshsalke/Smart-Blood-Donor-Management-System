"""
Admin Blueprint - Admin dashboard and management
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, send_file
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.donor import Donor
from app.models.blood_request import BloodRequest
from app.models.donation import Donation
from app.models.hospital import Hospital
from app.models.admin_log import AdminLog
from app.services.geo_service import GeoService
from app.services.export_service import ExportService
from app.services.ml_service import MLService
from datetime import datetime, timedelta
import pandas as pd
import json

admin_bp = Blueprint('admin', __name__, template_folder='templates')

def admin_required(f):
    """Decorator to require admin privileges"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard"""
    # Get statistics
    total_users = User.query.count()
    total_donors = Donor.query.count()
    total_requests = BloodRequest.query.count()
    total_donations = Donation.query.count()
    
    # Recent activity
    recent_donors = Donor.query.order_by(Donor.created_at.desc()).limit(5).all()
    recent_requests = BloodRequest.query.order_by(BloodRequest.created_at.desc()).limit(5).all()
    recent_donations = Donation.query.order_by(Donation.created_at.desc()).limit(5).all()
    
    # Request status breakdown
    pending_requests = BloodRequest.query.filter_by(status='pending').count()
    fulfilled_requests = BloodRequest.query.filter_by(status='fulfilled').count()
    emergency_requests = BloodRequest.query.filter_by(urgency='emergency', status='pending').count()
    
    # Chart data
    # Donations by month
    last_6_months = []
    donations_data = []
    for i in range(5, -1, -1):
        month = datetime.now() - timedelta(days=30*i)
        month_name = month.strftime('%b %Y')
        last_6_months.append(month_name)
        
        count = Donation.query.filter(
            Donation.donation_date >= month,
            Donation.donation_date < month + timedelta(days=30)
        ).count()
        donations_data.append(count)
    
    # Blood type distribution
    blood_types = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    blood_type_counts = []
    for bt in blood_types:
        count = Donor.query.filter_by(blood_type=bt).count()
        blood_type_counts.append(count)
    
    return render_template('admin/dashboard.html',
                         stats={
                             'total_users': total_users,
                             'total_donors': total_donors,
                             'total_requests': total_requests,
                             'total_donations': total_donations,
                             'pending_requests': pending_requests,
                             'fulfilled_requests': fulfilled_requests,
                             'emergency_requests': emergency_requests
                         },
                         recent_donors=recent_donors,
                         recent_requests=recent_requests,
                         recent_donations=recent_donations,
                         chart_labels=json.dumps(last_6_months),
                         chart_data=json.dumps(donations_data),
                         blood_types=json.dumps(blood_types),
                         blood_type_counts=json.dumps(blood_type_counts),
                         title='Admin Dashboard')

@admin_bp.route('/donors')
@login_required
@admin_required
def manage_donors():
    """Manage donors"""
    donors = Donor.query.all()
    return render_template('admin/manage_donors.html',
                         donors=donors,
                         title='Manage Donors')

# @admin_bp.route('/donors/toggle/<int:donor_id>')
# @login_required
# @admin_required
# def toggle_donor_status(donor_id):
#     """Activate/deactivate donor"""
#     donor = Donor.query.get_or_404(donor_id)
#     donor.is_active = not donor.is_active
    
#     # Log action
#     log = AdminLog(
#         admin_id=current_user.id,
#         admin_email=current_user.email,
#         action='UPDATE',
#         entity_type='DONOR',
#         entity_id=str(donor_id),
#         description=f"Toggled donor status to {'active' if donor.is_active else 'inactive'}",
#         ip_address=request.remote_addr
#     )
#     db.session.add(log)
#     db.session.commit()
    
#     flash(f"Donor {'activated' if donor.is_active else 'deactivated'} successfully", 'success')
#     return redirect(url_for('admin.manage_donors'))

@admin_bp.route('/donors/toggle/<int:donor_id>')
@login_required
@admin_required
def toggle_donor_status(donor_id):
    """Activate/deactivate donor (toggles user's is_active status)"""
    donor = Donor.query.get_or_404(donor_id)
    user = donor.user
    
    # Toggle user's active status (not donor's)
    user.is_active = not user.is_active
    
    # Log action
    log = AdminLog(
        admin_id=current_user.id,
        admin_email=current_user.email,
        action='UPDATE',
        entity_type='DONOR',
        entity_id=str(donor_id),
        description=f"Toggled donor status to {'active' if user.is_active else 'inactive'}",
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()
    
    flash(f"Donor {'activated' if user.is_active else 'deactivated'} successfully", 'success')
    return redirect(url_for('admin.manage_donors'))

@admin_bp.route('/bulk-email', methods=['GET', 'POST'])
@login_required
@admin_required
def bulk_email():
    """Send bulk email to selected donors"""
    donor_ids = request.args.get('ids', '').split(',')
    donor_ids = [int(id) for id in donor_ids if id]
    
    donors = Donor.query.filter(Donor.id.in_(donor_ids)).all()
    
    if request.method == 'POST':
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        if not subject or not message:
            flash('Subject and message are required', 'danger')
            return redirect(url_for('admin.bulk_email', ids=','.join(map(str, donor_ids))))
        
        # Send emails
        from app.services.email_service import EmailService
        success_count = 0
        
        for donor in donors:
            if donor.user and donor.user.email:
                # Create dashboard message
                from app.services.message_service import MessageService
                MessageService.send_message(
                    recipient_id=donor.user_id,
                    subject=subject,
                    content=message,
                    message_type='notification'
                )
                
                # Send email
                if EmailService.send_notification(donor.user.email, subject, message):
                    success_count += 1
        
        # Log action
        log = AdminLog(
            admin_id=current_user.id,
            admin_email=current_user.email,
            action='BULK_EMAIL',
            entity_type='DONOR',
            description=f"Sent bulk email to {success_count} donors",
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        
        flash(f'Bulk email sent to {success_count} donors successfully', 'success')
        return redirect(url_for('admin.manage_donors'))
    
    return render_template('admin/bulk_email.html', 
                         donors=donors,
                         donor_ids=','.join(map(str, donor_ids)),
                         title='Bulk Email')

@admin_bp.route('/requests')
@login_required
@admin_required
def manage_requests():
    """Manage blood requests"""
    requests = BloodRequest.query.order_by(BloodRequest.created_at.desc()).all()
    return render_template('admin/manage_requests.html',
                         requests=requests,
                         title='Manage Requests')

@admin_bp.route('/requests/delete/<int:request_id>')
@login_required
@admin_required
def delete_request(request_id):
    """Delete blood request"""
    blood_request = BloodRequest.query.get_or_404(request_id)
    
    # Log action
    log = AdminLog(
        admin_id=current_user.id,
        admin_email=current_user.email,
        action='DELETE',
        entity_type='REQUEST',
        entity_id=blood_request.request_id,
        description=f"Deleted request for {blood_request.blood_type_needed}",
        ip_address=request.remote_addr
    )
    db.session.add(log)
    
    db.session.delete(blood_request)
    db.session.commit()
    
    flash('Request deleted successfully', 'success')
    return redirect(url_for('admin.manage_requests'))

@admin_bp.route('/hospitals')
@login_required
@admin_required
def manage_hospitals():
    """Manage hospitals"""
    hospitals = Hospital.query.all()
    return render_template('admin/manage_hospitals.html',
                         hospitals=hospitals,
                         title='Manage Hospitals')

@admin_bp.route('/hospitals/add', methods=['POST'])
@login_required
@admin_required
def add_hospital():
    """Add new hospital"""
    try:
        hospital = Hospital(
            name=request.form.get('name'),
            phone=request.form.get('phone'),
            email=request.form.get('email'),
            address=request.form.get('address'),
            city=request.form.get('city'),
            state=request.form.get('state'),
            pincode=request.form.get('pincode'),
            latitude=float(request.form.get('latitude')),
            longitude=float(request.form.get('longitude')),
            hospital_type=request.form.get('hospital_type'),
            has_blood_bank=request.form.get('has_blood_bank') == 'on',
            contact_person_name=request.form.get('contact_person_name'),
            contact_person_phone=request.form.get('contact_person_phone')
        )
        
        db.session.add(hospital)
        
        # Log action
        log = AdminLog(
            admin_id=current_user.id,
            admin_email=current_user.email,
            action='CREATE',
            entity_type='HOSPITAL',
            entity_id=hospital.hospital_id,
            description=f"Added hospital: {hospital.name}",
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        
        flash('Hospital added successfully', 'success')
    except Exception as e:
        flash(f'Error adding hospital: {str(e)}', 'danger')
    
    return redirect(url_for('admin.manage_hospitals'))

@admin_bp.route('/activity-logs')
@login_required
@admin_required
def activity_logs():
    """View admin activity logs"""
    logs = AdminLog.query.order_by(AdminLog.created_at.desc()).limit(100).all()
    return render_template('admin/activity_logs.html',
                         logs=logs,
                         title='Activity Logs')

@admin_bp.route('/map-dashboard')
@login_required
@admin_required
def map_dashboard():
    """Map analytics dashboard"""
    donors = Donor.query.filter(Donor.latitude.isnot(None), Donor.longitude.isnot(None)).all()
    hospitals = Hospital.query.filter(Hospital.latitude.isnot(None), Hospital.longitude.isnot(None)).all()
    
    return render_template('admin/map_dashboard.html',
                         donors=donors,
                         hospitals=hospitals,
                         title='Map Dashboard')

@admin_bp.route('/demand-forecast')
@login_required
@admin_required
def demand_forecast():
    """Blood demand forecast"""
    ml_service = MLService()
    
    # Get forecast for all blood types
    forecasts = []
    blood_types = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    
    for bt in blood_types:
        forecast = ml_service.forecast_demand(blood_type=bt, months_ahead=3)
        forecasts.extend(forecast)
    
    return render_template('admin/demand_forecast.html',
                         forecasts=forecasts,
                         title='Demand Forecast')


@admin_bp.route('/donors/edit/<int:donor_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_donor(donor_id):
    """Edit donor details"""
    donor = Donor.query.get_or_404(donor_id)
    user = donor.user
    
    if request.method == 'POST':
        # Update user fields
        user.name = request.form.get('name')
        user.email = request.form.get('email')
        user.phone = request.form.get('phone')
        
        # Update donor fields
        donor.blood_type = request.form.get('blood_type')
        donor.address = request.form.get('address')
        donor.city = request.form.get('city')
        donor.state = request.form.get('state')
        donor.pincode = request.form.get('pincode')
        donor.emergency_contact_name = request.form.get('emergency_contact_name')
        donor.emergency_contact_phone = request.form.get('emergency_contact_phone')
        donor.emergency_contact_relation = request.form.get('emergency_contact_relation')
        donor.medical_conditions = request.form.get('medical_conditions')
        donor.medications = request.form.get('medications')
        donor.is_available = 'is_available' in request.form
        donor.is_eligible = 'is_eligible' in request.form
        
        db.session.commit()
        
        # Log action
        log = AdminLog(
            admin_id=current_user.id,
            admin_email=current_user.email,
            action='UPDATE',
            entity_type='DONOR',
            entity_id=str(donor_id),
            description=f"Updated donor {donor.user.name}",
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        
        flash('Donor updated successfully', 'success')
        return redirect(url_for('admin.manage_donors'))
    
    return render_template('admin/edit_donor.html', 
                         donor=donor, 
                         user=user,
                         title='Edit Donor')


@admin_bp.route('/requests/fulfill/<request_id>', methods=['POST'])
@login_required
@admin_required
def fulfill_request(request_id):
    """Mark a blood request as fulfilled"""
    try:
        blood_request = BloodRequest.query.filter_by(request_id=request_id).first_or_404()
        
        if blood_request.status == 'pending':
            blood_request.status = 'fulfilled'
            blood_request.fulfilled_at = datetime.utcnow()
            
            # Log action
            log = AdminLog(
                admin_id=current_user.id,
                admin_email=current_user.email,
                action='UPDATE',
                entity_type='REQUEST',
                entity_id=request_id,
                description=f"Marked request {request_id} as fulfilled",
                ip_address=request.remote_addr
            )
            db.session.add(log)
            db.session.commit()
            
            return jsonify({'status': 'success', 'message': 'Request marked as fulfilled'})
        else:
            return jsonify({'status': 'error', 'message': f'Request is already {blood_request.status}'}), 400
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@admin_bp.route('/requests/cancel/<request_id>', methods=['POST'])
@login_required
@admin_required
def cancel_request(request_id):
    """Cancel a blood request"""
    try:
        blood_request = BloodRequest.query.filter_by(request_id=request_id).first_or_404()
        
        if blood_request.status == 'pending':
            blood_request.status = 'cancelled'
            
            # Log action
            log = AdminLog(
                admin_id=current_user.id,
                admin_email=current_user.email,
                action='UPDATE',
                entity_type='REQUEST',
                entity_id=request_id,
                description=f"Cancelled request {request_id}",
                ip_address=request.remote_addr
            )
            db.session.add(log)
            db.session.commit()
            
            return jsonify({'status': 'success', 'message': 'Request cancelled successfully'})
        else:
            return jsonify({'status': 'error', 'message': f'Cannot cancel request with status {blood_request.status}'}), 400
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@admin_bp.route('/export/<entity_type>')
@login_required
@admin_required
def export_data(entity_type):
    """Export data to CSV"""
    export_service = ExportService()
    
    if entity_type == 'donors':
        data = Donor.query.all()
        filename = export_service.export_donors(data)
    elif entity_type == 'requests':
        data = BloodRequest.query.all()
        filename = export_service.export_requests(data)
    elif entity_type == 'donations':
        data = Donation.query.all()
        filename = export_service.export_donations(data)
    else:
        flash('Invalid export type', 'danger')
        return redirect(url_for('admin.dashboard'))
    
    # Log export
    log = AdminLog(
        admin_id=current_user.id,
        admin_email=current_user.email,
        action='EXPORT',
        entity_type=entity_type.upper(),
        description=f"Exported {entity_type} data",
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()
    
    if filename and os.path.exists(filename):
        return send_file(
            filename,
            as_attachment=True,
            download_name=f"{entity_type}_{datetime.now().strftime('%Y%m%d')}.csv",
            mimetype='text/csv'
        )
    else:
        flash('Export failed', 'danger')
        return redirect(url_for('admin.dashboard'))

import os