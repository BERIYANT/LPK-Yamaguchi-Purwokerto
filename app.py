from flask import Flask
# from flask_wtf.csrf import CSRFProtect  # removed
import os
from config import Config

# Import security middleware
from middleware.security_headers import setup_csp

from flask import Flask, make_response, request  # Tambahkan import request

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY

# Provide a safe fallback for csrf_token() in templates
app.jinja_env.globals['csrf_token'] = lambda: ''

# Add custom Jinja2 filter untuk format time
def format_time(value):
    """Format time value (handles both datetime.time and timedelta objects)"""
    if value is None:
        return ''
    # Jika value adalah string
    if isinstance(value, str):
        return value
    # Jika value adalah timedelta (dari MySQL TIME)
    if hasattr(value, 'total_seconds'):
        total_seconds = int(value.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours:02d}:{minutes:02d}"
    # Jika value adalah datetime.time
    if hasattr(value, 'strftime'):
        return value.strftime('%H:%M')
    return str(value)

app.jinja_env.filters['format_time'] = format_time

# Add custom Jinja2 filter untuk format currency (Rupiah)
def format_currency(value):
    """Format value sebagai currency Rupiah"""
    if value is None:
        return 'Rp 0'
    try:
        return f"Rp {int(value):,}".replace(',', '.')
    except (ValueError, TypeError):
        return f"Rp {value}"

app.jinja_env.filters['format_currency'] = format_currency

# Upload config
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = Config.UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH

# Setup Content Security Policy
setup_csp(app)

# Import dan register blueprints
from controllers.auth_controller import auth_bp
from controllers.admin_controller import admin_bp
from controllers.teacher_controller import teacher_bp
from controllers.student_controller import student_bp
from controllers.material_controller import material_bp
from controllers.quiz_controller import quiz_bp
from controllers.assignment_controller import assignment_bp
from controllers.forum_controller import forum_bp
from controllers.certificate_controller import certificate_bp
from controllers.job_controller import job_bp
from controllers.attendance_controller import attendance_bp
from controllers.question_bank_controller import question_bank_bp

# HAPUS BARIS-BARIS INI - route admin sudah ditangani oleh admin_bp
# app.add_url_rule('/admin/payments', view_func=payments, methods=['GET'])
# app.add_url_rule('/admin/verify-payment', view_func=verify_payment, methods=['POST'])
# app.add_url_rule('/admin/reject-payment', view_func=reject_payment, methods=['POST'])
# app.add_url_rule('/admin/payment-detail', view_func=payment_detail, methods=['GET'])

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(teacher_bp, url_prefix='/teacher')
app.register_blueprint(student_bp, url_prefix='/student')
app.register_blueprint(material_bp)
app.register_blueprint(quiz_bp)
app.register_blueprint(assignment_bp)
app.register_blueprint(forum_bp)
app.register_blueprint(certificate_bp)
app.register_blueprint(job_bp)
app.register_blueprint(attendance_bp)
app.register_blueprint(question_bank_bp, url_prefix='/teacher/bank')

# Import dan register middleware
from middleware.auth_middleware import load_user
from middleware.error_handler import register_error_handlers
from utils.file_handler import normalize_path

app.before_request(load_user)
app.teardown_appcontext(lambda e: None)  # Database handling di dalam fungsi
register_error_handlers(app)

# Jinja2 filters
@app.template_filter('normalize_path')
def normalize_path_filter(file_path):
    return normalize_path(file_path)

# Import routes utama
from routes_main import *

@app.after_request
def override_csp_for_emailjs(response):
    # Hanya untuk halaman contact yang butuh EmailJS
    if request.endpoint in ['main.home', 'main.contact']:
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' https://cdn.jsdelivr.net 'unsafe-inline'; connect-src 'self' https://api.emailjs.com https://*.emailjs.com;"
    return response

if __name__ == '__main__':
    app.run(debug=false)