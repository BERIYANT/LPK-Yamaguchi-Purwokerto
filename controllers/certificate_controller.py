from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g, send_file, current_app, send_from_directory
from utils.authentication import login_required
from models.certificate_model import CertificateModel
import os

certificate_bp = Blueprint('certificate', __name__)

@certificate_bp.route('/certificate/<int:certificate_id>')
@login_required
def view_certificate(certificate_id):
    cert = CertificateModel.get_by_id(certificate_id)
    if not cert:
        flash("Sertifikat tidak ditemukan.")
        return redirect(url_for('admin.dashboard'))
    
    # Resolve current user safely
    current_user = getattr(g, 'user', None)
    role = (current_user.get('role') if isinstance(current_user, dict) else None) or session.get('role')
    # Cast to int to avoid string/int mismatch
    user_id_val = (current_user.get('id') if isinstance(current_user, dict) else None) or session.get('user_id')
    try:
        user_id_int = int(user_id_val) if user_id_val is not None else None
    except:
        user_id_int = None

    if role == 'student' and user_id_int is not None and int(cert['student_id']) != user_id_int:
        flash("Anda tidak memiliki akses ke sertifikat ini.")
        return redirect(url_for('admin.dashboard'))
    
    # Untuk menampilkan detail satu sertifikat di template daftar, bungkus cert dalam list
    return render_template('admin/view_certificates.html', certificates=[cert])

@certificate_bp.route('/certificate/<int:certificate_id>/download')
@login_required
def download_certificate(certificate_id):
    cert = CertificateModel.get_by_id(certificate_id)
    if not cert:
        flash("Sertifikat tidak ditemukan.")
        return redirect(url_for('admin.dashboard'))

    current_user = getattr(g, 'user', None)
    role = (current_user.get('role') if isinstance(current_user, dict) else None) or session.get('role')
    user_id_val = (current_user.get('id') if isinstance(current_user, dict) else None) or session.get('user_id')
    try:
        user_id_int = int(user_id_val) if user_id_val is not None else None
    except:
        user_id_int = None

    # Allow only owner if student; admins/sensei bypass
    if role == 'student' and user_id_int is not None and int(cert['student_id']) != user_id_int:
        flash("Anda tidak memiliki akses ke sertifikat ini.")
        return redirect(url_for('admin.dashboard'))

    if not cert.get('file_path'):
        flash("Sertifikat ini tidak memiliki file.")
        return redirect(url_for('student.my_certificates'))

    try:
        fp = cert['file_path'] or ''
        # Normalize relative path
        rel_path = fp[8:] if fp.startswith('uploads/') else fp

        app_root = current_app.root_path
        abs_candidates = [
            os.path.join(app_root, 'static', 'uploads', rel_path),
            os.path.join(app_root, 'static', rel_path),
        ]

        # Try absolute filesystem paths
        for abs_path in abs_candidates:
            if os.path.exists(abs_path) and os.path.isfile(abs_path):
                file_ext = rel_path.split('.')[-1] if '.' in rel_path else 'pdf'
                download_name = f"Sertifikat_{(cert.get('certificate_number') or 'Unduhan').replace(' ', '_')}.{file_ext}"
                return send_file(abs_path, as_attachment=True, download_name=download_name)

        # Fallback: try serving from static directory safely
        for static_rel in [f"uploads/{rel_path}", rel_path]:
            safe_rel = static_rel.replace('\\', '/').lstrip('/')
            static_dir = os.path.join(app_root, 'static')
            candidate = os.path.join(static_dir, safe_rel)
            if os.path.exists(candidate) and os.path.isfile(candidate):
                file_ext = safe_rel.split('.')[-1] if '.' in safe_rel else 'pdf'
                download_name = f"Sertifikat_{(cert.get('certificate_number') or 'Unduhan').replace(' ', '_')}.{file_ext}"
                return send_from_directory(static_dir, safe_rel, as_attachment=True, download_name=download_name)

        flash("File sertifikat tidak ditemukan di server.")
        return redirect(url_for('student.my_certificates'))

    except Exception as e:
        flash(f"Error saat mengunduh file: {str(e)}")
        return redirect(url_for('student.my_certificates'))