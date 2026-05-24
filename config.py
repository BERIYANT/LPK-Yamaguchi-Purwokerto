import os

class Config:
    # Basic Config
    SECRET_KEY = "lpk-yamaguchi-production-2024-secret-key-#@!$%^&*"
    
    # Upload Config
    UPLOAD_FOLDER = "static/uploads"
    MAX_CONTENT_LENGTH = 4 * 1024 * 1024  # 4MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'txt', 'zip', 'rar'}
    
    # Database configuration
    DB_CONFIG = {
    'host': 'localhost',
    'user': 'lpkd3153_lpk_yamaguchi-pwt',      
    'password': 'Terserah27!',                  
    'database': 'lpkd3153_elearning_lpkyamaguchi' 
}
    
    # CSRF Protection
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = "lpk-yamaguchi-csrf-secret-2024-#@!$%^&*"
    
    # Security Headers
    CSP_ENABLED = True
    HSTS_ENABLED = True
    
    # Session Security
    SESSION_COOKIE_SECURE = True  # Hanya HTTPS
    SESSION_COOKIE_HTTPONLY = True  # Tidak bisa diakses JavaScript
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
    
    # Production vs Development
    ENV = 'production'  # atau 'development'