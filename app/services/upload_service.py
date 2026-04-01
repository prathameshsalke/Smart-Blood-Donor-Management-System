"""
Upload Service - Handle file uploads during registration and profile updates
"""

import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import current_app
from PIL import Image
import base64
import io

class UploadService:
    """Service for handling file uploads"""
    
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    
    def __init__(self):
        self.upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'profiles')
        os.makedirs(self.upload_folder, exist_ok=True)
    
    def allowed_file(self, filename):
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS
    
    def generate_filename(self, donor_unique_id, source='upload'):
        """Generate unique filename for uploaded photo"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        return f"donor_{donor_unique_id}_{source}_{timestamp}_{unique_id}.jpg"
    
    def save_uploaded_file(self, file, donor_unique_id):
        """Save uploaded file during registration or profile update"""
        if not file or not file.filename:
            return {'success': False, 'error': 'No file provided'}
        
        if not self.allowed_file(file.filename):
            return {'success': False, 'error': 'File type not allowed. Allowed: PNG, JPG, JPEG, GIF'}
        
        # Check file size
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)
        
        if size > self.MAX_FILE_SIZE:
            max_size_mb = self.MAX_FILE_SIZE // (1024 * 1024)
            return {'success': False, 'error': f'File too large. Maximum size is {max_size_mb}MB'}
        
        # Generate filename and save
        filename = self.generate_filename(donor_unique_id, 'reg')
        filepath = os.path.join(self.upload_folder, filename)
        file.save(filepath)
        
        # Optimize image
        self.optimize_image(filepath)
        
        return {
            'success': True,
            'filename': filename,
            'path': f"uploads/profiles/{filename}"
        }
    
    def save_base64_image(self, base64_data, donor_unique_id):
        """Save base64 encoded image from camera"""
        try:
            # Remove data URL prefix if present
            if ',' in base64_data:
                base64_data = base64_data.split(',')[1]
            
            # Decode base64
            image_bytes = base64.b64decode(base64_data)
            
            # Generate filename
            filename = self.generate_filename(donor_unique_id, 'camera')
            filepath = os.path.join(self.upload_folder, filename)
            
            # Save and optimize image
            img = Image.open(io.BytesIO(image_bytes))
            
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            # Resize if too large
            if img.size[0] > 800 or img.size[1] > 800:
                img.thumbnail((800, 800), Image.Resampling.LANCZOS)
            
            # Save with optimization
            img.save(filepath, 'JPEG', quality=85, optimize=True)
            
            return {
                'success': True,
                'filename': filename,
                'path': f"uploads/profiles/{filename}"
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def optimize_image(self, filepath, max_size=(800, 800), quality=85):
        """Optimize image size and dimensions"""
        try:
            img = Image.open(filepath)
            
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            # Resize if too large
            if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Save with optimization
            img.save(filepath, 'JPEG', quality=quality, optimize=True)
            
        except Exception as e:
            print(f"Image optimization error: {e}")
    
    def delete_photo(self, photo_path):
        """Delete old profile photo"""
        if photo_path:
            full_path = os.path.join(current_app.root_path, 'static', photo_path)
            if os.path.exists(full_path):
                try:
                    os.remove(full_path)
                    return True
                except:
                    pass
        return False