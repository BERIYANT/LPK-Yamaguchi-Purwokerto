from flask import request, current_app
from functools import wraps

def setup_csp(app):
    """Setup Content Security Policy untuk aplikasi"""
    
    @app.after_request
    def set_security_headers(response):
        # Content Security Policy yang diperbaiki
        csp_policy = (
            "default-src 'self'; "
            # Script sources - PERBAIKI domain
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' "
            "https://cdn.jsdelivr.net https://cdnjs.cloudflare.com "
            "https://cdn.voiceflow.com https://general-runtime.voiceflow.com "
            "https://runtime-api.voiceflow.com https://cdn.voicelore.com "
            "blob:; "  # PERLU untuk blob URLs
            # Style sources
            "style-src 'self' 'unsafe-inline' "
            "https://cdnjs.cloudflare.com https://cdn.jsdelivr.net "
            "https://fonts.googleapis.com https://cdn.voiceflow.com; "
            # Font sources
            "font-src 'self' https://cdnjs.cloudflare.com https://fonts.gstatic.com; "
            # Image sources
            "img-src 'self' data: https: blob:; "
            # Connect sources (AJAX, WebSocket)
            "connect-src 'self' https://api.emailjs.com https://*.emailjs.com "
            "https://general-runtime.voiceflow.com https://runtime-api.voiceflow.com "
            "https://api.voiceflow.com ws: wss:; "
            # Worker sources - PENTING untuk VoiceFlow audio
            "worker-src 'self' blob: https://cdn.voiceflow.com; "
            # Frame sources
            "frame-src 'self' https:; "
            # Media sources (audio/video)
            "media-src 'self' blob: https:; "
            # Lainnya
            "frame-ancestors 'self'; "
            "base-uri 'self'; "
            "form-action 'self'; "
            "object-src 'none'; "
        )
        
        # Security Headers
        response.headers['Content-Security-Policy'] = csp_policy
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        return response

def csp_exempt(f):
    """Decorator untuk exempt CSP pada route tertentu jika diperlukan"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Tambahkan header untuk exempt CSP jika diperlukan
        return f(*args, **kwargs)
    return decorated_function