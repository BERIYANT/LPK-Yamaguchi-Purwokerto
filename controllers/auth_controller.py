from flask import Blueprint, render_template, request, redirect, url_for, session, flash, g, jsonify, Response
from werkzeug.security import check_password_hash, generate_password_hash
from utils.authentication import login_required, admin_required
from forms import LoginForm, RegisterForm, ChangePasswordForm
import re
import os
from datetime import datetime
import uuid

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    
    if form.validate_on_submit():
        username = form.username.data.strip()
        password = form.password.data
        
        from models.user_model import UserModel
        user = UserModel.get_by_username(username)
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session.pop('selected_class_id', None)
            flash("Login berhasil.", "success")
            
            # Redirect berdasarkan role
            if user['role'] == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif user['role'] == 'sensei':
                return redirect(url_for('teacher.dashboard'))
            else:
                return redirect(url_for('student.dashboard'))
                
        flash("Username atau password salah.", "danger")
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("Anda sudah logout.")
    return redirect(url_for('index'))

@auth_bp.route('/register-student', methods=['GET', 'POST'])
def register_student():
    """Public registration for prospective students with program selection and payment"""
    if g.user:
        flash("Anda sudah login.", "info")
        return redirect(url_for('student.dashboard'))
    
    from models.user_model import UserModel
    from models.program_model import ProgramModel
    from models.payment_model import PaymentModel
    
    # Get all active programs (hanya ada 2: Reguler dan Karyawan)
    programs = ProgramModel.get_all_active()
    
    if request.method == 'POST':
        try:
            # Collect form data
            form_data = {
                'full_name': request.form.get('full_name', '').strip(),
                'email': request.form.get('email', '').strip(),
                'phone': request.form.get('phone', '').strip(),
                'gender': request.form.get('gender', ''),
                'birth_place': request.form.get('birth_place', '').strip(),
                'birth_date': request.form.get('birth_date', ''),
                'address': request.form.get('address', '').strip(),
                
                # New PDF-specific fields
                'nik': request.form.get('nik', '').strip(),
                'height': request.form.get('height', type=int) or None,
                'weight': request.form.get('weight', type=int) or None,
                'blood_type': request.form.get('blood_type', '').strip(),
                'father_name': request.form.get('father_name', '').strip(),
                'mother_name': request.form.get('mother_name', '').strip(),
                'parent_phone': request.form.get('parent_phone', '').strip(),
                'parent_address': request.form.get('parent_address', '').strip(),
                'sd_year': request.form.get('sd_year', '').strip(),
                'smp_year': request.form.get('smp_year', '').strip(),
                'sma_year': request.form.get('sma_year', '').strip(),
                'd3_year': request.form.get('d3_year', '').strip(),
                
                'education': request.form.get('education', ''),
                'major': request.form.get('major', '').strip(),
                'selected_class_type': request.form.get('selected_class_type', ''),
                'learning_purpose': request.form.get('learning_purpose', '').strip(),
                'experience': request.form.get('experience', ''),
                'agreeTerms': request.form.get('agreeTerms')
            }
            
            # Validations
            errors = []
            
            # Required field validations (tanpa username dan password)
            required_fields = [
                'full_name', 'email', 'phone', 'gender', 'birth_place', 
                'birth_date', 'address', 'selected_class_type', 'agreeTerms',
                'nik', 'height', 'weight', 'father_name', 'mother_name', 
                'parent_phone', 'parent_address', 'sma_year', 'education'
            ]
            
            for field in required_fields:
                if not form_data.get(field):
                    field_display = field.replace('_', ' ').title()
                    if field == 'agreeTerms':
                        field_display = 'Persetujuan Syarat'
                    elif field == 'selected_class_type':
                        field_display = 'Jenis Kelas'
                    errors.append(f"{field_display} harus diisi")
            
            # Email validation
            email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if form_data['email'] and not re.match(email_regex, form_data['email']):
                errors.append("Format email tidak valid")
            
            # Phone validation
            if form_data['phone']:
                phone_digits = re.sub(r'\D', '', form_data['phone'])
                if not phone_digits or len(phone_digits) < 10 or len(phone_digits) > 13:
                    errors.append("Nomor telepon harus 10-13 digit")
            
            # Check if email already exists
            existing_user_by_email = UserModel.get_by_email(form_data['email'])
            if existing_user_by_email:
                errors.append("Email sudah terdaftar")
            
            # Check file uploads
            ktp_file = request.files.get('ktp_file')
            pas_file = request.files.get('pas_file')
            payment_proof = request.files.get('payment_proof')
            ijazah_file = request.files.get('ijazah_file')
            
            if not ktp_file or not ktp_file.filename:
                errors.append("Foto KTP harus diupload")
            
            if not pas_file or not pas_file.filename:
                errors.append("Foto Pas 3x4 harus diupload")
            
            if not payment_proof or not payment_proof.filename:
                errors.append("Bukti pembayaran harus diupload")
            
            if errors:
                for error in errors:
                    flash(error, "danger")
                return render_template('auth/register_student.html', programs=programs, form_data=form_data)
            
            # Get program based on class type
            program = ProgramModel.get_by_class_type(form_data['selected_class_type'])
            if not program:
                flash("Program tidak ditemukan untuk kelas yang dipilih", "danger")
                return render_template('auth/register_student.html', programs=programs, form_data=form_data)
            
            # Generate username automatically (email without domain + random number)
            email_prefix = form_data['email'].split('@')[0]
            random_suffix = str(uuid.uuid4().int)[:4]  # 4 random digits
            generated_username = f"{email_prefix}_{random_suffix}"
            
            # Generate temporary password (will be changed by admin)
            generated_password = str(uuid.uuid4().int)[:8]  # 8 random digits
            hashed_password = generate_password_hash(generated_password)
            
            from utils.database import get_db
            db = get_db()
            cur = db.cursor()
            
            try:
                # Generate unique filenames
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                ktp_filename = None
                pas_filename = None
                ijazah_filename = None
                payment_proof_filename = None
                
                # Create uploads directory if not exists
                upload_dir = os.path.join('static', 'uploads')
                if not os.path.exists(upload_dir):
                    os.makedirs(upload_dir)
                
                # Save uploaded files
                if ktp_file and ktp_file.filename:
                    file_ext = os.path.splitext(ktp_file.filename)[1]
                    ktp_filename = f"ktp_{generated_username}_{timestamp}{file_ext}"
                    ktp_path = os.path.join(upload_dir, ktp_filename)
                    ktp_file.save(ktp_path)
                
                if pas_file and pas_file.filename:
                    file_ext = os.path.splitext(pas_file.filename)[1]
                    pas_filename = f"pas_{generated_username}_{timestamp}{file_ext}"
                    pas_path = os.path.join(upload_dir, pas_filename)
                    pas_file.save(pas_path)
                
                if ijazah_file and ijazah_file.filename:
                    file_ext = os.path.splitext(ijazah_file.filename)[1]
                    ijazah_filename = f"ijazah_{generated_username}_{timestamp}{file_ext}"
                    ijazah_path = os.path.join(upload_dir, ijazah_filename)
                    ijazah_file.save(ijazah_path)
                
                if payment_proof and payment_proof.filename:
                    file_ext = os.path.splitext(payment_proof.filename)[1]
                    payment_proof_filename = f"payment_{generated_username}_{timestamp}{file_ext}"
                    payment_path = os.path.join(upload_dir, payment_proof_filename)
                    payment_proof.save(payment_path)
                
                # Create user with student role
                cur.execute("""
                    INSERT INTO users (username, email, phone, password, role, full_name, 
                    birth_place, birth_date, address, nik, height, weight, blood_type, 
                    father_name, mother_name, parent_phone, parent_address, sd_year, 
                    smp_year, sma_year, d3_year, education, major, program_id, 
                    selected_class_type, learning_purpose, experience, ktp_file, 
                    pas_foto_file, ijazah_file, payment_status, registration_completed)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending_verification', 0)
                """, (
                    generated_username,
                    form_data['email'],
                    form_data['phone'],
                    hashed_password,
                    'student',
                    form_data['full_name'],
                    form_data['birth_place'],
                    form_data['birth_date'],
                    form_data['address'],
                    
                    form_data['nik'],
                    form_data['height'],
                    form_data['weight'],
                    form_data['blood_type'],
                    form_data['father_name'],
                    form_data['mother_name'],
                    form_data['parent_phone'],
                    form_data['parent_address'],
                    form_data['sd_year'],
                    form_data['smp_year'],
                    form_data['sma_year'],
                    form_data['d3_year'],
                    
                    form_data['education'],
                    form_data['major'],
                    program['id'],
                    form_data['selected_class_type'],
                    form_data['learning_purpose'],
                    form_data['experience'],
                    ktp_filename,
                    pas_filename,
                    ijazah_filename
                ))
                
                user_id = cur.lastrowid
                
                # HANYA BUAT 1 RECORD PEMBAYARAN UNTUK PENDAFTARAN SAJA
                # (Pendaftaran + Pra MCU sebesar Rp 350,000)
                registration_amount = float(program['registration_fee'])
                
                # Gunakan PaymentModel dari models.payment_model
                payment_id = PaymentModel.create(
                    user_id=user_id,
                    program_id=program['id'],
                    payment_type='registration',  # Hanya 'registration' saja
                    amount=registration_amount,
                    proof_file=payment_proof_filename,
                    status='pending'
                )
                
                # TIDAK BUAT RECORD LAINNYA (pre_mcu, education_installment_1, dll)
                # Biaya-biaya lainnya akan dibuat nanti oleh admin setelah verifikasi
                
                db.commit()
                
                # Simpan data untuk notifikasi ke admin (tidak menampilkan password ke user)
                session['pending_registration_email'] = form_data['email']
                session['pending_registration_username'] = generated_username
                
                flash("Pendaftaran berhasil! Admin akan memverifikasi data dan mengirimkan username/password ke email Anda.", "success")
                return render_template('auth/register_student.html', 
                                     registration_success=True,
                                     email=form_data['email'],
                                     programs=programs,
                                     pending_username=generated_username)
                
            except Exception as e:
                db.rollback()
                flash(f"Terjadi kesalahan: {str(e)}", "danger")
                return render_template('auth/register_student.html', programs=programs, form_data=form_data)
            finally:
                cur.close()
                
        except Exception as e:
            flash(f"Terjadi kesalahan: {str(e)}", "danger")
            return render_template('auth/register_student.html', programs=programs)
    
    # GET request - show form
    return render_template('auth/register_student.html', programs=programs)

@auth_bp.route('/download-registration-pdf/<username>')
def download_registration_pdf(username):
    # Authorization: Match session or logged-in admin
    if session.get('pending_registration_username') != username and not (g.user and g.user.get('role') == 'admin'):
        flash("Tidak diizinkan mengunduh formulir ini.", "danger")
        return redirect(url_for('index'))
        
    from models.user_model import UserModel
    user = UserModel.get_by_username(username)
    if not user:
        flash("Pengguna tidak ditemukan.", "danger")
        return redirect(url_for('index'))
        
    from utils.pdf_generator import generate_registration_pdf
    
    # Format date to string if it's a date object
    birth_date = user.get('birth_date')
    if hasattr(birth_date, 'strftime'):
        birth_date = birth_date.strftime('%d-%m-%Y')
        
    import io
    from flask import send_file
    
    pdf_bytes = generate_registration_pdf({
        'full_name': user.get('full_name'),
        'birth_place': user.get('birth_place'),
        'birth_date': birth_date,
        'address': user.get('address'),
        'phone': user.get('phone'),
        'major': user.get('major'),
        'education': user.get('education'),
        
        # New PDF fields
        'nik': user.get('nik'),
        'height': user.get('height'),
        'weight': user.get('weight'),
        'blood_type': user.get('blood_type'),
        'father_name': user.get('father_name'),
        'mother_name': user.get('mother_name'),
        'parent_phone': user.get('parent_phone'),
        'parent_address': user.get('parent_address'),
        'sd_year': user.get('sd_year'),
        'smp_year': user.get('smp_year'),
        'sma_year': user.get('sma_year'),
        'd3_year': user.get('d3_year')
    })
    
    is_preview = request.args.get('preview', '0') == '1'
    
    return send_file(
        io.BytesIO(bytes(pdf_bytes)),
        mimetype='application/pdf',
        as_attachment=not is_preview,
        download_name=f"Formulir_Pendaftaran_{username}.pdf"
    )

@auth_bp.route('/register', methods=['GET', 'POST'])
@login_required
@admin_required
def register():
    from models.class_model import ClassModel
    from models.user_model import UserModel
    
    classes = ClassModel.get_all()
    
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        full_name = request.form.get('full_name', '').strip()
        role = request.form.get('role', 'student')
        class_id = request.form.get('class_id')

        # Check if username already exists
        existing_user = UserModel.get_by_username(username)
        if existing_user:
            flash("Username sudah digunakan.")
            return render_template('auth/register.html', classes=classes)

        try:
            user_id = UserModel.create_user(username, password, role, full_name)
            
            # Auto-enroll for students
            if class_id and role == 'student':
                from utils.database import get_db
                db = get_db()
                cur = db.cursor()
                cur.execute("INSERT INTO enrollments (user_id, class_id) VALUES (%s, %s)", (user_id, class_id))
                db.commit()
                cur.close()
            
            flash(f"User {username} berhasil didaftarkan sebagai {role}.")
            return redirect(url_for('admin.users'))
        except Exception as e:
            flash(f"Error: {str(e)}")
    
    return render_template('auth/register.html', classes=classes)

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    from models.user_model import UserModel
    
    if request.method == 'POST':
        current = request.form.get('current_password', '')
        newp = request.form.get('new_password', '')
        newp2 = request.form.get('new_password_confirm', '')

        if not check_password_hash(g.user['password'], current):
            flash('Password saat ini salah.')
            return redirect(url_for('auth.change_password'))
        
        if not newp or newp != newp2:
            flash('Konfirmasi password tidak cocok atau password baru kosong.')
            return redirect(url_for('auth.change_password'))

        UserModel.update_password(g.user['id'], newp)
        flash('Password berhasil diubah.')
        return redirect(url_for('profile'))

    return render_template('auth/change_password.html')

