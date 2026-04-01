"""
Export Service - Handle data export to various formats
"""

import csv
import json
import os
import pandas as pd
from datetime import datetime
from flask import current_app

class ExportService:
    """Service for exporting data"""
    
    def __init__(self):
        self.export_dir = os.path.join(current_app.root_path, 'static/exports')
        os.makedirs(self.export_dir, exist_ok=True)
    
    def export_donors(self, donors, filename=None):
        """Export donors to CSV"""
        if not filename:
            filename = f"donors_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        filepath = os.path.join(self.export_dir, filename)
        
        # Prepare data
        data = []
        for donor in donors:
            data.append({
                'ID': donor.id,
                'Name': donor.user.name if donor.user else '',
                'Email': donor.user.email if donor.user else '',
                'Phone': donor.user.phone if donor.user else '',
                'Blood Type': donor.blood_type,
                'Age': donor.calculate_age() if hasattr(donor, 'calculate_age') else '',
                'Gender': donor.gender,
                'Weight': donor.weight,
                'Address': donor.address,
                'City': donor.city,
                'State': donor.state,
                'Pincode': donor.pincode,
                'Latitude': donor.latitude,
                'Longitude': donor.longitude,
                'Total Donations': donor.total_donations,
                'Last Donation': donor.last_donation_date.strftime('%Y-%m-%d') if donor.last_donation_date else '',
                'Eligible': 'Yes' if donor.is_eligible else 'No',
                'Available': 'Yes' if donor.is_available else 'No',
                'Medical Conditions': donor.medical_conditions or '',
                'Medications': donor.medications or '',
                'Emergency Contact': donor.emergency_contact_name or '',
                'Emergency Phone': donor.emergency_contact_phone or '',
                'Emergency Relation': donor.emergency_contact_relation or '',
                'Nationality': donor.nationality or 'Indian',
                'Has Disability': 'Yes' if donor.has_disability else 'No',
                'Disability': donor.disability or '',
                'Created At': donor.created_at.strftime('%Y-%m-%d %H:%M') if donor.created_at else ''
            })
        
        # Write to CSV
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            if data:
                fieldnames = data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
        
        return filepath
    
    def export_hospitals(self, hospitals, filename=None):
        """Export hospitals to CSV"""
        if not filename:
            filename = f"hospitals_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        filepath = os.path.join(self.export_dir, filename)
        
        # Prepare data
        data = []
        for hospital in hospitals:
            data.append({
                'ID': hospital.id,
                'Hospital ID': hospital.hospital_id,
                'Name': hospital.name,
                'Phone': hospital.phone,
                'Email': hospital.email or '',
                'Emergency Phone': hospital.emergency_phone or '',
                'Address': hospital.address,
                'City': hospital.city,
                'State': hospital.state,
                'Pincode': hospital.pincode,
                'Latitude': hospital.latitude,
                'Longitude': hospital.longitude,
                'Type': hospital.hospital_type or '',
                'Has Blood Bank': 'Yes' if hospital.has_blood_bank else 'No',
                'Verified': 'Yes' if hospital.is_verified else 'No',
                'Registration Number': hospital.registration_number or '',
                'License Number': hospital.license_number or '',
                'Contact Person': hospital.contact_person_name or '',
                'Contact Designation': hospital.contact_person_designation or '',
                'Contact Phone': hospital.contact_person_phone or '',
                'Website': hospital.website or '',
                'Created At': hospital.created_at.strftime('%Y-%m-%d') if hospital.created_at else ''
            })
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            if data:
                fieldnames = data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
        
        return filepath
    
    def export_requests(self, requests, filename=None):
        """Export blood requests to CSV"""
        if not filename:
            filename = f"requests_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        filepath = os.path.join(self.export_dir, filename)
        
        data = []
        for req in requests:
            data.append({
                'Request ID': req.request_id,
                'Patient': req.patient_name,
                'Patient Age': req.patient_age or '',
                'Patient Gender': req.patient_gender or '',
                'Blood Type': req.blood_type_needed,
                'Units': req.units_needed,
                'Urgency': req.urgency,
                'Status': req.status,
                'Hospital': req.hospital_name or '',
                'Requester': req.requester_name,
                'Requester Phone': req.requester_phone,
                'Requester Email': req.requester_email or '',
                'Reason': req.reason or '',
                'Latitude': req.requester_latitude,
                'Longitude': req.requester_longitude,
                'Search Radius': req.search_radius,
                'Notified Donors': req.notified_donors,
                'Accepted Donors': req.accepted_donors,
                'Created': req.created_at.strftime('%Y-%m-%d %H:%M') if req.created_at else '',
                'Expires': req.expires_at.strftime('%Y-%m-%d %H:%M') if req.expires_at else '',
                'Fulfilled': req.fulfilled_at.strftime('%Y-%m-%d %H:%M') if req.fulfilled_at else ''
            })
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            if data:
                fieldnames = data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
        
        return filepath
    
    def export_donations(self, donations, filename=None):
        """Export donations to CSV"""
        if not filename:
            filename = f"donations_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        filepath = os.path.join(self.export_dir, filename)
        
        data = []
        for donation in donations:
            data.append({
                'Donation ID': donation.donation_id,
                'Donor ID': donation.donor_id,
                'Donor Name': donation.donor_name,
                'Blood Type': donation.donor_blood_type,
                'Units': donation.units_donated,
                'Date': donation.donation_date.strftime('%Y-%m-%d %H:%M') if donation.donation_date else '',
                'Location': donation.donation_center or '',
                'Address': donation.donation_center_address or '',
                'Blood Pressure': donation.blood_pressure or '',
                'Hemoglobin': donation.hemoglobin_level or '',
                'Verified': 'Yes' if donation.is_verified else 'No',
                'Verified By': donation.verified_by or '',
                'Verified At': donation.verified_at.strftime('%Y-%m-%d %H:%M') if donation.verified_at else '',
                'Certificate': 'Yes' if donation.certificate_generated else 'No',
                'Notes': donation.notes or '',
                'Request ID': donation.request_ref or ''
            })
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            if data:
                fieldnames = data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
        
        return filepath
    
    def export_to_excel(self, data, sheet_name, filename=None):
        """Export data to Excel"""
        if not filename:
            filename = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        filepath = os.path.join(self.export_dir, filename)
        
        df = pd.DataFrame(data)
        df.to_excel(filepath, sheet_name=sheet_name, index=False)
        
        return filepath
    
    def export_to_json(self, data, filename=None):
        """Export data to JSON"""
        if not filename:
            filename = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = os.path.join(self.export_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as jsonfile:
            json.dump(data, jsonfile, indent=2, default=str)
        
        return filepath
    
    def cleanup_old_exports(self, days=7):
        """Delete export files older than specified days"""
        import time
        cutoff = time.time() - (days * 24 * 60 * 60)
        count = 0
        
        if os.path.exists(self.export_dir):
            for filename in os.listdir(self.export_dir):
                filepath = os.path.join(self.export_dir, filename)
                if os.path.isfile(filepath) and os.path.getmtime(filepath) < cutoff:
                    os.remove(filepath)
                    count += 1
        
        return count