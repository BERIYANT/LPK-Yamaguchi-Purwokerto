import os
from werkzeug.utils import secure_filename
from datetime import datetime
from flask import current_app  # IMPORT current_app

# Hapus config import jika tidak digunakan
# from config import Config  # Komentari ini jika tidak perlu

# Definisikan ALLOWED_EXTENSIONS di sini
ALLOWED_EXTENSIONS = {
    'png', 'jpg', 'jpeg', 'gif',  # Images
    'pdf', 'doc', 'docx', 'txt',  # Documents
    'mp3', 'wav', 'ogg', 'm4a',   # Audio - PASTIKAN INI ADA
    'mp4', 'avi', 'mov'           # Video
}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def normalize_path(file_path):
    """Normalize file path untuk cross-platform compatibility"""
    if file_path:
        if file_path.startswith('static/') or file_path.startswith('static\\'):
            file_path = file_path.replace('static/', '').replace('static\\', '')
        return file_path.replace('\\', '/')
    return file_path

def save_uploaded_file(file, subfolder=""):
    """Save uploaded file with timestamp and unique name"""
    if file and allowed_file(file.filename):
        # Cek extension audio
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        safe_name = f"{subfolder}_{timestamp}_{filename}"
        
        # Pastikan folder uploads ada
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        
        file_path = os.path.join(upload_folder, safe_name)
        file.save(file_path)
        
        # Kembalikan relative path untuk disimpan di database
        return os.path.join('uploads', safe_name)
    return None