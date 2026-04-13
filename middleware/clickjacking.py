from flask import request, Response, current_app
from functools import wraps

def anti_clickjacking(f):
    """Decorator untuk mencegah clickjacking"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        response = f(*args, **kwargs)
        
        # Tambahkan headers anti-clickjacking
        if isinstance(response, Response):
            response.headers['X-Frame-Options'] = 'SAMEORIGIN'
            response.headers['Content-Security-Policy'] = "frame-ancestors 'self';"
        else:
            # Jika return string atau template, buat Response object
            response = current_app.make_response(response)
            response.headers['X-Frame-Options'] = 'SAMEORIGIN'
            response.headers['Content-Security-Policy'] = "frame-ancestors 'self';"
        
        return response
    return decorated_function

def frame_options_exempt(f):
    """Decorator untuk exempt frame options jika diperlukan (untuk embed tertentu)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        response = f(*args, **kwargs)
        if isinstance(response, Response):
            response.headers.pop('X-Frame-Options', None)
            # Allow from specific domains jika diperlukan
            # response.headers['Content-Security-Policy'] = "frame-ancestors 'self' https://trusted-domain.com;"
        return response
    return decorated_function