"""
Certificate Service for generating donation certificates
"""

import os
import qrcode
import threading
import time
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from flask import current_app, url_for
from apscheduler.schedulers.background import BackgroundScheduler

# Import db from app
from app import db
from app.services.message_service import MessageService
from app.services.email_service import EmailService

class CertificateService:
    """Service for generating donation certificates"""
    
    def __init__(self):
        self.certificate_folder = current_app.config['CERTIFICATE_FOLDER']
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
    
    def generate_donation_certificate(self, donation):
        """
        Generate PDF certificate for a donation
        Schedules notification to be sent after 1 minute
        """
        try:
            # Create unique filename
            filename = f"cert_{donation.donation_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            filepath = os.path.join(self.certificate_folder, filename)
            
            # Create PDF document
            doc = SimpleDocTemplate(
                filepath,
                pagesize=landscape(A4),
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18,
            )
            
            # Container for the 'Flowable' objects
            elements = []
            
            # Styles
            styles = getSampleStyleSheet()
            title_style = styles['Title']
            title_style.textColor = colors.HexColor('#8B0000')  # Dark red
            
            heading_style = styles['Heading2']
            normal_style = styles['Normal']
            
            # Create custom style for certificate
            cert_style = ParagraphStyle(
                'CertStyle',
                parent=styles['Normal'],
                fontSize=14,
                leading=20,
                alignment=1,  # Center alignment
                spaceAfter=30,
            )
            
            # Add certificate header
            elements.append(Paragraph("BLOOD DONATION CERTIFICATE", title_style))
            elements.append(Spacer(1, 0.5*inch))
            
            # Add certificate number
            elements.append(Paragraph(f"Certificate No: {donation.donation_id}", normal_style))
            elements.append(Spacer(1, 0.3*inch))
            
            # Add main text
            main_text = f"""
            This is to certify that <b>{donation.donor_name}</b> has voluntarily donated blood 
            on <b>{donation.donation_date.strftime('%B %d, %Y')}</b> at <b>{donation.donation_center or 'Blood Donation Camp'}</b>.
            """
            elements.append(Paragraph(main_text, cert_style))
            elements.append(Spacer(1, 0.3*inch))
            
            # Add donation details
            details = [
                ['Blood Group:', donation.donor_blood_type],
                ['Units Donated:', str(donation.units_donated)],
                ['Donation ID:', donation.donation_id],
                ['Date:', donation.donation_date.strftime('%B %d, %Y at %I:%M %p')],
            ]
            
            if donation.blood_pressure:
                details.append(['Blood Pressure:', donation.blood_pressure])
            if donation.hemoglobin_level:
                details.append(['Hemoglobin Level:', f"{donation.hemoglobin_level} g/dL"])
            
            # Create table for details
            table = Table(details, colWidths=[2*inch, 3*inch])
            table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 12),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#8B0000')),
                ('PADDING', (0, 0), (-1, -1), 6),
            ]))
            
            elements.append(table)
            elements.append(Spacer(1, 0.5*inch))
            
            # Generate QR Code
            qr_data = f"Donation ID: {donation.donation_id}\nDonor: {donation.donor_name}\nDate: {donation.donation_date}"
            qr_filename = f"qr_{donation.donation_id}.png"
            qr_path = os.path.join(self.certificate_folder, qr_filename)
            self.generate_qr_code(qr_data, qr_path)
            
            # Add QR code to certificate
            if os.path.exists(qr_path):
                qr_image = Image(qr_path, width=1.5*inch, height=1.5*inch)
                elements.append(qr_image)
                donation.qr_code_path = qr_path
            
            elements.append(Spacer(1, 0.2*inch))
            elements.append(Paragraph("Scan QR code to verify certificate", normal_style))
            elements.append(Spacer(1, 0.5*inch))
            
            # Add signature line
            signature_table = Table([
                ['____________________', '____________________'],
                ['Authorized Signatory', 'Date']
            ], colWidths=[3*inch, 3*inch])
            signature_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.grey),
            ]))
            
            elements.append(signature_table)
            
            # Build PDF
            doc.build(elements)
            
            # Update donation record
            donation.certificate_path = filepath
            donation.certificate_generated = True
            db.session.commit()
            
            # Schedule notification after 1 minute
            self.schedule_notification(donation)
            
            return filepath
            
        except Exception as e:
            current_app.logger.error(f"Certificate generation error: {e}")
            return None
    
    def schedule_notification(self, donation):
        """Schedule certificate notification after 1 minute"""
        def send_notification():
            time.sleep(60)  # Wait 1 minute
            with current_app.app_context():
                # Send dashboard notification
                MessageService.send_certificate_notification(donation)
                
                # Send email
                EmailService.send_certificate_notification(donation)
        
        # Run in background thread
        thread = threading.Thread(target=send_notification)
        thread.daemon = True
        thread.start()
    
    def generate_qr_code(self, data, filepath):
        """Generate QR code for certificate verification"""
        try:
            qr = qrcode.QRCode(
                version=1,
                box_size=10,
                border=5
            )
            qr.add_data(data)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            img.save(filepath)
            
            return filepath
            
        except Exception as e:
            current_app.logger.error(f"QR code generation error: {e}")
            return None
    
    def verify_certificate(self, donation_id):
        """Verify certificate by donation ID"""
        from app.models.donation import Donation
        donation = Donation.query.filter_by(donation_id=donation_id).first()
        
        if donation:
            return {
                'valid': True,
                'donor_name': donation.donor_name,
                'blood_type': donation.donor_blood_type,
                'donation_date': donation.donation_date.strftime('%B %d, %Y'),
                'verified': donation.is_verified
            }
        return {'valid': False, 'message': 'Invalid certificate ID'}