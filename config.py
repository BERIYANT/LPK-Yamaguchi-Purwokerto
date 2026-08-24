import os

class Config:
    # Basic Config
    SECRET_KEY = os.getenv("SECRET_KEY", "lpk-yamaguchi-local-dev")
    
    # Upload Config
    UPLOAD_FOLDER = "static/uploads"
    MAX_CONTENT_LENGTH = 4 * 1024 * 1024  # 4MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'txt', 'zip', 'rar'}
    
    # Database configuration
    DB_CONFIG = {
        'host': os.getenv('DB_HOST', '127.0.0.1'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', 'root'),
        'database': os.getenv('DB_NAME', 'elearning_lpkyamaguchi'),
        'port': int(os.getenv('DB_PORT', '3306')),
    }
    
    # CSRF Protection
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = "lpk-yamaguchi-csrf-secret-2024-#@!$%^&*"
    
    # Security Headers
    CSP_ENABLED = True
    HSTS_ENABLED = True
    
    # Session Security
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'false').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True  # Tidak bisa diakses JavaScript
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
    
    # Production vs Development
    ENV = os.getenv('FLASK_ENV', 'development')