from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask import session, flash, redirect, url_for, g

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not g.user:
            flash("Silakan login terlebih dahulu.")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return wrapper

def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not g.user:
            flash("Silakan login terlebih dahulu.")
            return redirect(url_for('auth.login'))
        
        if g.user.get('role') != 'admin':
            flash("Akses ditolak. Hanya admin yang dapat mengakses halaman ini.")
            # Redirect ke dashboard sesuai role
            if g.user.get('role') == 'sensei':
                return redirect(url_for('teacher.dashboard'))
            else:
                return redirect(url_for('student.dashboard'))
        
        return f(*args, **kwargs)
    return wrapper

def teacher_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not g.user:
            flash("Silakan login terlebih dahulu.")
            return redirect(url_for('auth.login'))
        
        if g.user.get('role') != 'sensei':
            flash("Akses ditolak. Hanya sensei yang dapat mengakses halaman ini.")
            # Redirect ke dashboard sesuai role
            if g.user.get('role') == 'admin':
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('student.dashboard'))
        
        return f(*args, **kwargs)
    return wrapper

def class_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if g.user.get('role') == 'sensei' and not session.get('selected_class_id'):
            flash("Silakan pilih kelas terlebih dahulu.")
            return redirect(url_for('teacher.dashboard'))
        return f(*args, **kwargs)
    return wrapper