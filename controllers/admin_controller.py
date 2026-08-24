from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g, jsonify
from utils.authentication import login_required, admin_required
from models.user_model import UserModel
from models.class_model import ClassModel
from models.certificate_model import CertificateModel
from werkzeug.security import generate_password_hash
from datetime import datetime
from utils.database import get_db

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    from utils.database import get_db
    db = get_db()
    cur = db.cursor(dictionary=True)
    
    cur.execute("SELECT COUNT(*) as total FROM users WHERE role='student'")
    total_students = cur.fetchone()['total']
    
    cur.execute("SELECT COUNT(*) as total FROM users WHERE role='sensei'")
    total_teachers = cur.fetchone()['total']
    
    cur.execute("SELECT COUNT(*) as total FROM classes")
    active_classes = cur.fetchone()['total']
    
    cur.execute("SELECT COUNT(*) as total FROM certificates")
    total_certificates = cur.fetchone()['total']
    
    # Student Activities (Left) - Same structure as activities page
    student_activities = []
    try:
        cur.execute("""
            SELECT u.username, u.full_name, 'Mengerjakan Kuis' as activity, 
                   CONCAT('Nilai: ', qs.score) as detail, qs.graded_at as timestamp
            FROM quiz_scores qs
            JOIN users u ON qs.student_id = u.id
            UNION ALL
            SELECT u.username, u.full_name, 'Upload Tugas', 
                   CONCAT('Tugas ID: ', ts.task_id), ts.submitted_at
            FROM task_submissions ts
            JOIN users u ON ts.student_id = u.id
            ORDER BY timestamp DESC
            LIMIT 10
        """)
        student_activities = cur.fetchall()
    except:
        pass
    
    # Teacher Activities (Right) - Same structure as activities page
    teacher_activities = []
    try:
        cur.execute("""
            SELECT u.username, u.full_name, 'Membuat Materi' as activity, m.title as detail, m.created_at as timestamp
            FROM materials m
            JOIN users u ON m.created_by = u.id
            UNION ALL
            SELECT u.username, u.full_name, 'Membuat Kuis', q.title, q.created_at
            FROM quizzes q
            JOIN users u ON q.created_by = u.id
            UNION ALL
            SELECT u.username, u.full_name, 'Membuat Tugas', t.title, t.created_at
            FROM tasks t
            JOIN users u ON t.created_by = u.id
            ORDER BY timestamp DESC
            LIMIT 10
        """)
        teacher_activities = cur.fetchall()
    except:
        pass
    
    # Pending Tasks
    pending_tasks = []
    
    # Count ungraded task submissions
    try:
        cur.execute("""
            SELECT COUNT(*) as total
            FROM task_submissions
            WHERE grade IS NULL
        """)
        ungraded = cur.fetchone()['total']
        if ungraded > 0:
            pending_tasks.append({
                'title': 'Tugas belum dinilai',
                'count': ungraded
            })
    except:
        pass
    
    # Count ungraded quiz submissions
    try:
        cur.execute("""
            SELECT COUNT(*) as total
            FROM quiz_scores
            WHERE reviewed = 0
        """)
        unreviewed = cur.fetchone()['total']
        if unreviewed > 0:
            pending_tasks.append({
                'title': 'Quiz perlu review',
                'count': unreviewed
            })
    except:
        pass
    
    # Count students without class
    try:
        cur.execute("""
            SELECT COUNT(DISTINCT u.id) as total
            FROM users u
            LEFT JOIN enrollments e ON u.id = e.user_id
            WHERE u.role = 'student' AND e.id IS NULL
        """)
        no_class = cur.fetchone()['total']
        if no_class > 0:
            pending_tasks.append({
                'title': 'Siswa belum dikelas',
                'count': no_class
            })
    except:
        pass
    
    cur.close()
    
    return render_template('admin/dashboard.html',
                         total_students=total_students,
                         total_teachers=total_teachers,
                         active_classes=active_classes,
                         total_certificates=total_certificates,
                         student_activities=student_activities,
                         teacher_activities=teacher_activities,
                         pending_tasks=pending_tasks)

# UPDATED CODE FOR admin_bp.py
# Replace the existing users() function with this version

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    from utils.database import get_db
    db = get_db()
    cur = db.cursor(dictionary=True)
    
    # Teachers with activity stats
    cur.execute("""
        SELECT u.*, 
               COUNT(DISTINCT m.id) as total_materials,
               COUNT(DISTINCT q.id) as total_quizzes,
               COUNT(DISTINCT t.id) as total_tasks
        FROM users u
        LEFT JOIN materials m ON m.created_by = u.id
        LEFT JOIN quizzes q ON q.created_by = u.id
        LEFT JOIN tasks t ON t.created_by = u.id
        WHERE u.role = 'sensei'
        GROUP BY u.id
    """)
    teachers = cur.fetchall()
    
    # Students with performance stats
    cur.execute("""
        SELECT u.*, 
               MAX(c.name) as class_name,
               COUNT(DISTINCT qs.id) as total_quiz_taken,
               ROUND(AVG(qs.score), 2) as avg_score,
               COUNT(DISTINCT ts.id) as total_task_submitted
        FROM users u
        LEFT JOIN enrollments e ON e.user_id = u.id
        LEFT JOIN classes c ON c.id = e.class_id
        LEFT JOIN quiz_scores qs ON qs.student_id = u.id
        LEFT JOIN task_submissions ts ON ts.student_id = u.id
        WHERE u.role = 'student'
        GROUP BY u.id
    """)
    students = cur.fetchall()
    
    # Calculate statistics
    total_teachers = len(teachers)
    total_students = len(students)
    total_users = total_teachers + total_students
    
    # Count active users (all users with role sensei or student)
    # If you have an 'is_active' column, you can add: AND is_active = 1
    cur.execute("""
        SELECT COUNT(*) as total 
        FROM users 
        WHERE role IN ('sensei', 'student')
    """)
    active_users = cur.fetchone()['total']
    
    cur.close()
    
    return render_template('admin/users.html', 
                         teachers=teachers, 
                         students=students,
                         total_users=total_users,
                         total_teachers=total_teachers,
                         total_students=total_students,
                         active_users=active_users)


# ============================================
# ALTERNATIVE VERSION (More Efficient)
# ============================================
# If you want to calculate statistics directly from database without loading all records

@admin_bp.route('/users')
@login_required
@admin_required
def users_alternative():
    from utils.database import get_db
    db = get_db()
    cur = db.cursor(dictionary=True)
    
    # Get statistics first (more efficient)
    cur.execute("""
        SELECT 
            COUNT(CASE WHEN role = 'sensei' THEN 1 END) as total_teachers,
            COUNT(CASE WHEN role = 'student' THEN 1 END) as total_students,
            COUNT(*) as total_users
        FROM users 
        WHERE role IN ('sensei', 'student')
    """)
    stats = cur.fetchone()
    
    # Teachers with activity stats
    cur.execute("""
        SELECT u.*, 
               COUNT(DISTINCT m.id) as total_materials,
               COUNT(DISTINCT q.id) as total_quizzes,
               COUNT(DISTINCT t.id) as total_tasks
        FROM users u
        LEFT JOIN materials m ON m.created_by = u.id
        LEFT JOIN quizzes q ON q.created_by = u.id
        LEFT JOIN tasks t ON t.created_by = u.id
        WHERE u.role = 'sensei'
        GROUP BY u.id
    """)
    teachers = cur.fetchall()
    
    # Students with performance stats
    cur.execute("""
        SELECT u.*, 
               MAX(c.name) as class_name,
               COUNT(DISTINCT qs.id) as total_quiz_taken,
               ROUND(AVG(qs.score), 2) as avg_score,
               COUNT(DISTINCT ts.id) as total_task_submitted
        FROM users u
        LEFT JOIN enrollments e ON e.user_id = u.id
        LEFT JOIN classes c ON c.id = e.class_id
        LEFT JOIN quiz_scores qs ON qs.student_id = u.id
        LEFT JOIN task_submissions ts ON ts.student_id = u.id
        WHERE u.role = 'student'
        GROUP BY u.id
    """)
    students = cur.fetchall()
    
    cur.close()
    
    return render_template('admin/users.html', 
                         teachers=teachers, 
                         students=students,
                         total_users=stats['total_users'],
                         total_teachers=stats['total_teachers'],
                         total_students=stats['total_students'],
                         active_users=stats['total_users'])  # or add specific logic for active users


# ============================================
# IF YOU HAVE is_active COLUMN IN DATABASE
# ============================================
@admin_bp.route('/users')
@login_required
@admin_required
def users_with_active_status():
    from utils.database import get_db
    db = get_db()
    cur = db.cursor(dictionary=True)
    
    # Get statistics with active user count
    cur.execute("""
        SELECT 
            COUNT(CASE WHEN role = 'sensei' THEN 1 END) as total_teachers,
            COUNT(CASE WHEN role = 'student' THEN 1 END) as total_students,
            COUNT(*) as total_users,
            COUNT(CASE WHEN is_active = 1 THEN 1 END) as active_users
        FROM users 
        WHERE role IN ('sensei', 'student')
    """)
    stats = cur.fetchone()
    
    # Teachers with activity stats
    cur.execute("""
        SELECT u.*, 
               COUNT(DISTINCT m.id) as total_materials,
               COUNT(DISTINCT q.id) as total_quizzes,
               COUNT(DISTINCT t.id) as total_tasks
        FROM users u
        LEFT JOIN materials m ON m.created_by = u.id
        LEFT JOIN quizzes q ON q.created_by = u.id
        LEFT JOIN tasks t ON t.created_by = u.id
        WHERE u.role = 'sensei'
        GROUP BY u.id
    """)
    teachers = cur.fetchall()
    
    # Students with performance stats
    cur.execute("""
        SELECT u.*, 
               MAX(c.name) as class_name,
               COUNT(DISTINCT qs.id) as total_quiz_taken,
               ROUND(AVG(qs.score), 2) as avg_score,
               COUNT(DISTINCT ts.id) as total_task_submitted
        FROM users u
        LEFT JOIN enrollments e ON e.user_id = u.id
        LEFT JOIN classes c ON c.id = e.class_id
        LEFT JOIN quiz_scores qs ON qs.student_id = u.id
        LEFT JOIN task_submissions ts ON ts.student_id = u.id
        WHERE u.role = 'student'
        GROUP BY u.id
    """)
    students = cur.fetchall()
    
    cur.close()
    
    return render_template('admin/users.html', 
                         teachers=teachers, 
                         students=students,
                         total_users=stats['total_users'],
                         total_teachers=stats['total_teachers'],
                         total_students=stats['total_students'],
                         active_users=stats['active_users'])

@admin_bp.route('/user/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    from utils.database import get_db
    
    user = UserModel.get_by_id(user_id)
    if not user:
        flash("User tidak ditemukan.")
        return redirect(url_for('admin.users'))
    
    # Prevent admin from editing themselves
    if user_id == session.get('user_id'):
        flash("Anda tidak dapat mengedit data Anda sendiri dari halaman ini. Gunakan menu Profile.")
        return redirect(url_for('admin.users'))
    
    classes = ClassModel.get_all()
    
    if request.method == 'POST':
        username = request.form['username'].strip()
        full_name = request.form.get('full_name', '').strip()
        role = request.form.get('role', 'student')
        new_password = request.form.get('new_password', '').strip()
        class_id = request.form.get('class_id')
        
        # Check username uniqueness
        existing_user = UserModel.get_by_username(username)
        if existing_user and existing_user['id'] != user_id:
            flash("Username sudah digunakan oleh user lain.")
            return render_template('admin/edit_user.html', user=user, classes=classes)
        
        db = get_db()
        cur = db.cursor(dictionary=True)
        
        # Update user data
        if new_password:
            UserModel.update_password(user_id, new_password)
        
        UserModel.update_user(user_id, username, full_name, role)
        
        # Update enrollment for students
        if role == 'student':
            # Remove old enrollment
            cur.execute("DELETE FROM enrollments WHERE user_id=%s", (user_id,))
            # Add new enrollment if class_id provided
            if class_id:
                cur.execute("INSERT INTO enrollments (user_id, class_id) VALUES (%s, %s)", (user_id, class_id))
        else:
            # Remove all enrollments if not student
            cur.execute("DELETE FROM enrollments WHERE user_id=%s", (user_id,))
        
        db.commit()
        cur.close()
        
        flash(f"Data user {username} berhasil diperbarui.")
        return redirect(url_for('admin.users'))
    
    # Get current enrollment for student
    current_enrollment = None
    if user['role'] == 'student':
        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT class_id FROM enrollments WHERE user_id=%s LIMIT 1", (user_id,))
        current_enrollment = cur.fetchone()
        cur.close()
    
    return render_template('admin/edit_user.html', user=user, classes=classes, current_enrollment=current_enrollment)

@admin_bp.route('/user/<int:user_id>/delete')
@login_required
@admin_required
def delete_user(user_id):
    from utils.database import get_db
    
    user = UserModel.get_by_id(user_id)
    if not user:
        flash("User tidak ditemukan.")
        return redirect(url_for('admin.users'))
    
    # Prevent admin from deleting themselves
    if user_id == session.get('user_id'):
        flash("Anda tidak dapat menghapus akun Anda sendiri.")
        return redirect(url_for('admin.users'))
    
    db = get_db()
    cur = db.cursor()
    
    try:
        # Delete related data
        # Enrollments
        cur.execute("DELETE FROM enrollments WHERE user_id=%s", (user_id,))
        
        # Quiz answers and scores
        cur.execute("DELETE FROM quiz_answers WHERE student_id=%s", (user_id,))
        cur.execute("DELETE FROM quiz_scores WHERE student_id=%s", (user_id,))
        
        # Task submissions
        cur.execute("DELETE FROM task_submissions WHERE student_id=%s", (user_id,))
        
        # Forum posts and replies
        cur.execute("DELETE FROM forum_replies WHERE user_id=%s", (user_id,))
        cur.execute("DELETE FROM forum_posts WHERE user_id=%s", (user_id,))
        
        # Certificates
        cur.execute("DELETE FROM certificates WHERE student_id=%s", (user_id,))
        
        # Materials, quizzes, tasks created (if sensei)
        if user['role'] == 'sensei':
            # Delete materials
            cur.execute("DELETE FROM materials WHERE created_by=%s", (user_id,))
            
            # Delete quizzes with related data
            cur.execute("SELECT id FROM quizzes WHERE created_by=%s", (user_id,))
            quiz_ids = [row[0] for row in cur.fetchall()]
            for qid in quiz_ids:
                cur.execute("DELETE FROM quiz_answers WHERE quiz_id=%s", (qid,))
                cur.execute("DELETE FROM quiz_scores WHERE quiz_id=%s", (qid,))
                cur.execute("DELETE FROM quiz_questions WHERE quiz_id=%s", (qid,))
            cur.execute("DELETE FROM quizzes WHERE created_by=%s", (user_id,))
            
            # Delete tasks with submissions
            cur.execute("DELETE FROM task_submissions WHERE task_id IN (SELECT id FROM tasks WHERE created_by=%s)", (user_id,))
            cur.execute("DELETE FROM tasks WHERE created_by=%s", (user_id,))
        
        # Delete user
        cur.execute("DELETE FROM users WHERE id=%s", (user_id,))
        
        db.commit()
        flash(f"User {user['username']} dan semua data terkait berhasil dihapus.")
    except Exception as e:
        db.rollback()
        flash(f"Error menghapus user: {str(e)}")
    finally:
        cur.close()
    
    return redirect(url_for('admin.users'))

@admin_bp.route('/user/<int:user_id>/reset-password', methods=['GET', 'POST'])
@login_required
@admin_required
def reset_password(user_id):
    user = UserModel.get_by_id(user_id)
    if not user:
        flash("User tidak ditemukan.")
        return redirect(url_for('admin.users'))
    
    if request.method == 'POST':
        new_password = request.form.get('new_password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        if not new_password or not confirm_password:
            flash("Password tidak boleh kosong.")
            return render_template('admin/reset_password.html', user=user)
        
        if new_password != confirm_password:
            flash("Konfirmasi password tidak cocok.")
            return render_template('admin/reset_password.html', user=user)
        
        if len(new_password) < 6:
            flash("Password minimal 6 karakter.")
            return render_template('admin/reset_password.html', user=user)
        
        UserModel.update_password(user_id, new_password)
        flash(f"Password user {user['username']} berhasil direset.")
        return redirect(url_for('admin.users'))
    
    return render_template('admin/reset_password.html', user=user)

@admin_bp.route('/classes')
@login_required
@admin_required
def classes():
    from utils.database import get_db
    db = get_db()
    cur = db.cursor(dictionary=True)
    
    # Get all classes with student count and teacher info
    cur.execute("""
        SELECT c.*, 
               COUNT(DISTINCT e.user_id) as total_students,
               u.full_name as teacher_name,
               u.username as teacher_username
        FROM classes c
        LEFT JOIN enrollments e ON c.id = e.class_id
        LEFT JOIN users u ON c.teacher_id = u.id
        GROUP BY c.id
        ORDER BY c.name
    """)
    classes = cur.fetchall()
    
    cur.close()
    
    return render_template('admin/classes.html', classes=classes)

@admin_bp.route('/class/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_class():
    from utils.database import get_db
    db = get_db()
    cur = db.cursor(dictionary=True)
    
    # Get all teachers for dropdown
    cur.execute("SELECT id, username, full_name FROM users WHERE role='sensei' ORDER BY full_name")
    teachers = cur.fetchall()
    cur.close()
    
    if request.method == 'POST':
        name = request.form['name'].strip()
        teacher_id = request.form.get('teacher_id', '').strip() or None
        schedule = request.form.get('schedule', '').strip()
        description = request.form.get('description', '').strip()
        start_time = request.form.get('start_time', '').strip() or None
        end_time = request.form.get('end_time', '').strip() or None
        capacity = request.form.get('capacity', 15)
        
        # Validate capacity
        try:
            capacity = int(capacity)
            if capacity < 1 or capacity > 50:
                capacity = 15
        except:
            capacity = 15
        
        # Create class with teacher_id
        db = get_db()
        cur = db.cursor()
        try:
            cur.execute("""
                INSERT INTO classes (name, teacher_id, schedule, description, start_time, end_time, capacity, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (name, teacher_id, schedule, description, start_time, end_time, capacity, datetime.now()))
            db.commit()
            flash("Kelas berhasil ditambahkan.")
            return redirect(url_for('admin.classes'))
        except Exception as e:
            db.rollback()
            flash(f"Error: {str(e)}")
        finally:
            cur.close()
    
    return render_template('admin/create_class.html', teachers=teachers)

@admin_bp.route('/class/<int:class_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_class(class_id):
    from utils.database import get_db
    db = get_db()
    cur = db.cursor(dictionary=True)
    
    # Get class data with teacher info
    cur.execute("""
        SELECT c.*, 
               u.full_name as teacher_name,
               COUNT(DISTINCT e.user_id) as total_students
        FROM classes c
        LEFT JOIN users u ON c.teacher_id = u.id
        LEFT JOIN enrollments e ON c.id = e.class_id
        WHERE c.id = %s
        GROUP BY c.id
    """, (class_id,))
    class_data = cur.fetchone()
    
    if not class_data:
        flash("Kelas tidak ditemukan.")
        cur.close()
        return redirect(url_for('admin.classes'))
    
    # Get all teachers for dropdown
    cur.execute("SELECT id, username, full_name FROM users WHERE role='sensei' ORDER BY full_name")
    teachers = cur.fetchall()
    cur.close()
    
    if request.method == 'POST':
        name = request.form['name'].strip()
        teacher_id = request.form.get('teacher_id', '').strip() or None
        schedule = request.form.get('schedule', '').strip()
        description = request.form.get('description', '').strip()
        start_time = request.form.get('start_time', '').strip() or None
        end_time = request.form.get('end_time', '').strip() or None
        capacity = request.form.get('capacity', 15)
        
        # Validate capacity
        try:
            capacity = int(capacity)
            if capacity < 1 or capacity > 50:
                capacity = 15
        except:
            capacity = 15
        
        # Update class with teacher_id
        cur = db.cursor()
        try:
            cur.execute("""
                UPDATE classes 
                SET name=%s, teacher_id=%s, schedule=%s, description=%s, 
                    start_time=%s, end_time=%s, capacity=%s
                WHERE id=%s
            """, (name, teacher_id, schedule, description, start_time, end_time, capacity, class_id))
            db.commit()
            flash("Kelas berhasil diperbarui.")
            return redirect(url_for('admin.classes'))
        except Exception as e:
            db.rollback()
            flash(f"Error: {str(e)}")
        finally:
            cur.close()
    
    return render_template('admin/edit_class.html', class_data=class_data, teachers=teachers)

@admin_bp.route('/class/<int:class_id>/delete')
@login_required
@admin_required
def delete_class(class_id):
    from utils.database import get_db
    
    db = get_db()
    cur = db.cursor()
    
    try:
        # Delete related data first
        cur.execute("DELETE FROM enrollments WHERE class_id=%s", (class_id,))
        cur.execute("DELETE FROM materials WHERE class_id=%s", (class_id,))
        cur.execute("DELETE FROM quizzes WHERE class_id=%s", (class_id,))
        cur.execute("DELETE FROM tasks WHERE class_id=%s", (class_id,))
        cur.execute("UPDATE certificates SET class_id=NULL WHERE class_id=%s", (class_id,))
        cur.execute("DELETE FROM classes WHERE id=%s", (class_id,))
        
        db.commit()
        flash("Kelas berhasil dihapus beserta semua data terkait.")
    except Exception as e:
        db.rollback()
        flash(f"Error menghapus kelas: {str(e)}")
    finally:
        cur.close()
    
    return redirect(url_for('admin.classes'))

@admin_bp.route('/certificates')
@login_required
@admin_required
def certificates():
    certificates = CertificateModel.get_all()
    return render_template('admin/certificates.html', certificates=certificates)

@admin_bp.route('/certificate/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_certificate():
    from utils.database import get_db
    from utils.file_handler import allowed_file, save_uploaded_file
    import os
    
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT id, username, full_name FROM users WHERE role='student' ORDER BY full_name")
    students = cur.fetchall()
    cur.close()
    
    if request.method == 'POST':
        student_id = request.form['student_id']
        certificate_number = request.form['certificate_number'].strip()
        description = request.form.get('description', '').strip()
        file_path = None
        
        if not student_id:
            flash('Pilih siswa terlebih dahulu.')
            return render_template('admin/create_certificate.html', students=students)
        
        # Handle file upload
        file = request.files.get('file')
        if file and file.filename:
            if not allowed_file(file.filename):
                flash('Format file tidak diizinkan. Gunakan PDF, JPG, PNG, GIF, DOC, atau DOCX.')
                return render_template('admin/create_certificate.html', students=students)
            
            try:
                safe_name = f"cert_{certificate_number.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
                file_path = save_uploaded_file(file, f"cert_{certificate_number}")
            except Exception as e:
                flash(f'Gagal mengupload file: {str(e)}')
                return render_template('admin/create_certificate.html', students=students)
        
        try:
            CertificateModel.create(student_id, certificate_number, description, file_path)
            flash("Sertifikat berhasil dibuat.")
            return redirect(url_for('admin.certificates'))
        except Exception as e:
            flash(f'Error: {str(e)}')
            # Delete file if insert failed
            if file_path:
                try:
                    os.remove(os.path.join('static/uploads', file_path))
                except:
                    pass
    
    return render_template('admin/create_certificate.html', students=students)

@admin_bp.route('/certificate/<int:cert_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_certificate(cert_id):
    from utils.database import get_db
    from utils.file_handler import allowed_file, save_uploaded_file
    import os
    
    cert = CertificateModel.get_by_id(cert_id)
    if not cert:
        flash("Sertifikat tidak ditemukan.")
        return redirect(url_for('admin.certificates'))
    
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT id, username, full_name FROM users WHERE role='student' ORDER BY full_name")
    students = cur.fetchall()
    cur.close()
    
    if request.method == 'POST':
        student_id = request.form['student_id']
        certificate_number = request.form['certificate_number'].strip()
        description = request.form.get('description', '').strip()
        file_path = cert.get('file_path')
        
        if not student_id:
            flash('Pilih siswa terlebih dahulu.')
            return render_template('admin/create_certificate.html', students=students, cert=cert, edit=True)
        
        # Handle new file upload
        file = request.files.get('file')
        if file and file.filename:
            if not allowed_file(file.filename):
                flash('Format file tidak diizinkan. Gunakan PDF, JPG, PNG, GIF, DOC, atau DOCX.')
                return render_template('admin/create_certificate.html', students=students, cert=cert, edit=True)
            
            # Delete old file if exists
            if file_path:
                old_paths = [
                    os.path.join('static/uploads', file_path),
                    os.path.join('static/uploads', file_path.replace('uploads/', ''))
                ]
                for old_file in old_paths:
                    if os.path.exists(old_file):
                        try:
                            os.remove(old_file)
                            break
                        except:
                            pass
            
            # Upload new file
            try:
                safe_name = f"cert_{certificate_number.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
                file_path = save_uploaded_file(file, f"cert_{certificate_number}")
            except Exception as e:
                flash(f'Gagal mengupload file: {str(e)}')
                return render_template('admin/create_certificate.html', students=students, cert=cert, edit=True)
        
        # Option to remove file
        if request.form.get('remove_file') == 'yes' and file_path:
            old_paths = [
                os.path.join('static/uploads', file_path),
                os.path.join('static/uploads', file_path.replace('uploads/', ''))
            ]
            for old_file in old_paths:
                if os.path.exists(old_file):
                    try:
                        os.remove(old_file)
                        break
                    except:
                        pass
            file_path = None
        
        try:
            CertificateModel.update(cert_id, student_id, certificate_number, description, file_path)
            flash("Sertifikat berhasil diperbarui.")
            return redirect(url_for('admin.certificates'))
        except Exception as e:
            flash(f'Error: {str(e)}')
    
    return render_template('admin/create_certificate.html', students=students, cert=cert, edit=True)

@admin_bp.route('/certificate/<int:cert_id>/delete')
@login_required
@admin_required
def delete_certificate(cert_id):
    import os
    
    cert = CertificateModel.get_by_id(cert_id)
    if not cert:
        flash("Sertifikat tidak ditemukan.")
        return redirect(url_for('admin.certificates'))
    
    # Delete physical file if exists
    if cert.get('file_path'):
        file_path = cert['file_path']
        possible_paths = [
            os.path.join('static/uploads', file_path),
            os.path.join('static/uploads', file_path.replace('uploads/', ''))
        ]
        for path in possible_paths:
            if os.path.exists(path):
                try:
                    os.remove(path)
                    break
                except:
                    pass
    
    CertificateModel.delete(cert_id)
    flash("Sertifikat berhasil dihapus.")
    return redirect(url_for('admin.certificates'))

@admin_bp.route('/activities')
@login_required
@admin_required
def activities():
    from utils.database import get_db
    db = get_db()
    cur = db.cursor(dictionary=True)
    
    # Teacher activities
    cur.execute("""
        SELECT u.username, u.full_name, 'Membuat Materi' as activity, m.title as detail, m.created_at as timestamp
        FROM materials m
        JOIN users u ON m.created_by = u.id
        UNION ALL
        SELECT u.username, u.full_name, 'Membuat Kuis', q.title, q.created_at
        FROM quizzes q
        JOIN users u ON q.created_by = u.id
        UNION ALL
        SELECT u.username, u.full_name, 'Membuat Tugas', t.title, t.created_at
        FROM tasks t
        JOIN users u ON t.created_by = u.id
        ORDER BY timestamp DESC
        LIMIT 50
    """)
    teacher_activities = cur.fetchall()
    
    # Student activities
    cur.execute("""
        SELECT u.username, u.full_name, 'Mengerjakan Kuis' as activity, 
               CONCAT('Nilai: ', qs.score) as detail, qs.graded_at as timestamp
        FROM quiz_scores qs
        JOIN users u ON qs.student_id = u.id
        UNION ALL
        SELECT u.username, u.full_name, 'Upload Tugas', 
               CONCAT('Tugas ID: ', ts.task_id), ts.submitted_at
        FROM task_submissions ts
        JOIN users u ON ts.student_id = u.id
        ORDER BY timestamp DESC
        LIMIT 50
    """)
    student_activities = cur.fetchall()
    
    cur.close()
    
    return render_template('admin/activities.html', 
                         teacher_activities=teacher_activities,
                         student_activities=student_activities)

@admin_bp.route('/payments')
@login_required
@admin_required
def payments():
    """View and manage payments with filters and pagination"""
    import math
    
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Build filter query
    filters = []
    params = []
    
    status = request.args.get('status')
    if status:
        filters.append("p.status = %s")
        params.append(status)
    
    payment_type = request.args.get('payment_type')
    if payment_type:
        filters.append("p.payment_type = %s")
        params.append(payment_type)
    
    start_date = request.args.get('start_date')
    if start_date:
        filters.append("DATE(p.payment_date) >= %s")
        params.append(start_date)
    
    end_date = request.args.get('end_date')
    if end_date:
        filters.append("DATE(p.payment_date) <= %s")
        params.append(end_date)
    
    where_clause = " AND ".join(filters) if filters else "1=1"
    
    db = get_db()
    cur = db.cursor(dictionary=True)
    
    try:
        # Get stats - only count verified payments for total_amount
        cur.execute(f"""
            SELECT 
                COALESCE(SUM(CASE WHEN status = 'verified' THEN amount ELSE 0 END), 0) as total_amount,
                SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending_count,
                SUM(CASE WHEN status = 'verified' THEN 1 ELSE 0 END) as verified_count,
                SUM(CASE WHEN status = 'rejected' THEN 1 ELSE 0 END) as rejected_count
            FROM payments p
            WHERE {where_clause}
        """, tuple(params))
        stats = cur.fetchone()
        
        # Count total records for pagination
        cur.execute(f"""
            SELECT COUNT(*) as total 
            FROM payments p
            JOIN users u ON p.user_id = u.id
            WHERE {where_clause}
        """, tuple(params))
        total = cur.fetchone()['total']
        
        # Get payments with pagination
        offset = (page - 1) * per_page
        cur.execute(f"""
            SELECT p.*, u.full_name, u.email, u.phone, u.username,
                   COALESCE(pr.class_type, 'N/A') as class_type
            FROM payments p
            JOIN users u ON p.user_id = u.id
            LEFT JOIN programs pr ON p.program_id = pr.id
            WHERE {where_clause}
            ORDER BY p.payment_date DESC
            LIMIT %s OFFSET %s
        """, tuple(params + [per_page, offset]))
        payments = cur.fetchall()
        
    except Exception as e:
        print(f"Error loading payments: {str(e)}")
        flash(f"Terjadi kesalahan: {str(e)}", "danger")
        payments = []
        stats = {'total_amount': 0, 'pending_count': 0, 'verified_count': 0, 'rejected_count': 0}
        total = 0
    finally:
        cur.close()
    
    total_pages = math.ceil(total / per_page) if total > 0 else 1
    
    return render_template('admin/payments.html',
                         payments=payments,
                         current_page=page,
                         total_pages=total_pages,
                         total_amount=stats['total_amount'] or 0,
                         pending_count=stats['pending_count'] or 0,
                         verified_count=stats['verified_count'] or 0,
                         rejected_count=stats['rejected_count'] or 0)

@admin_bp.route('/verify-payment', methods=['POST'])
@login_required
@admin_required
def verify_payment():
    """Verify a payment - MUST return JSON"""
    try:
        db = get_db()
        cur = db.cursor(dictionary=True)
        
        # Get data from JSON body
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'Data tidak valid'
            }), 400
            
        payment_id = data.get('payment_id')
        
        if not payment_id:
            cur.close()
            return jsonify({
                'success': False,
                'message': 'Payment ID harus diisi'
            }), 400
        
        # Get payment info
        cur.execute("SELECT * FROM payments WHERE id = %s", (payment_id,))
        payment = cur.fetchone()
        
        if not payment:
            cur.close()
            return jsonify({
                'success': False,
                'message': 'Pembayaran tidak ditemukan'
            }), 404
        
        # Check if already rejected
        if payment['status'] == 'rejected':
            cur.close()
            return jsonify({
                'success': False,
                'message': 'Pembayaran yang sudah ditolak tidak dapat diverifikasi'
            }), 400
        
        # Check if already verified
        if payment['status'] == 'verified':
            cur.close()
            return jsonify({
                'success': False,
                'message': 'Pembayaran sudah diverifikasi sebelumnya'
            }), 400
        
        # Update payment status to verified
        cur.execute("""
            UPDATE payments 
            SET status = 'verified',
                verified_by = %s,
                verified_at = %s,
                rejection_reason = NULL
            WHERE id = %s
        """, (g.user['id'], datetime.now(), payment_id))
        
        # If this is registration payment, update user status
        if payment['payment_type'] == 'registration':
            cur.execute("""
                UPDATE users 
                SET payment_status = 'verified', 
                    registration_completed = 1 
                WHERE id = %s
            """, (payment['user_id'],))
        
        db.commit()
        cur.close()
        
        # IMPORTANT: Return JSON response, not redirect!
        return jsonify({
            'success': True,
            'message': 'Pembayaran berhasil diverifikasi',
            'payment_id': payment_id,
            'amount': float(payment['amount'])
        }), 200
        
    except Exception as e:
        if 'db' in locals():
            db.rollback()
        if 'cur' in locals():
            cur.close()
            
        print(f"Error verifying payment: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        }), 500

@admin_bp.route('/reject-payment', methods=['POST'])
@login_required
@admin_required
def reject_payment():
    """Reject a payment - MUST return JSON"""
    try:
        db = get_db()
        cur = db.cursor(dictionary=True)
        
        # Get data from form
        payment_id = request.form.get('payment_id')
        rejection_reason = request.form.get('rejection_reason', '').strip()
        
        if not payment_id or not rejection_reason:
            return jsonify({
                'success': False,
                'message': 'Payment ID dan alasan penolakan harus diisi'
            }), 400
        
        # Get payment info
        cur.execute("SELECT * FROM payments WHERE id = %s", (payment_id,))
        payment = cur.fetchone()
        
        if not payment:
            cur.close()
            return jsonify({
                'success': False,
                'message': 'Pembayaran tidak ditemukan'
            }), 404
        
        # Check if already verified
        if payment['status'] == 'verified':
            cur.close()
            return jsonify({
                'success': False,
                'message': 'Pembayaran yang sudah diverifikasi tidak dapat ditolak'
            }), 400
        
        # Update payment status to rejected
        cur.execute("""
            UPDATE payments 
            SET status = 'rejected', 
                verified_by = %s, 
                verified_at = %s,
                rejection_reason = %s
            WHERE id = %s
        """, (g.user['id'], datetime.now(), rejection_reason, payment_id))
        
        db.commit()
        cur.close()
        
        # IMPORTANT: Return JSON response, not redirect!
        return jsonify({
            'success': True,
            'message': 'Pembayaran berhasil ditolak',
            'payment_id': payment_id,
            'amount': float(payment['amount'])
        }), 200
        
    except Exception as e:
        if 'db' in locals():
            db.rollback()
        if 'cur' in locals():
            cur.close()
        
        print(f"Error rejecting payment: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        }), 500

@admin_bp.route('/payment-detail')
@login_required
@admin_required
def payment_detail():
    """Get payment detail HTML fragment for modal"""
    payment_id = request.args.get('payment_id')
    
    if not payment_id:
        return '<p class="text-danger" style="padding: 20px;">Payment ID tidak ditemukan</p>', 400
    
    db = get_db()
    cur = db.cursor(dictionary=True)
    
    try:
        # Get payment with user and program info
        cur.execute("""
            SELECT p.*, u.full_name, u.email, u.phone,
                   COALESCE(pr.class_type, 'N/A') as class_type,
                   admin.full_name as verified_by_name
            FROM payments p
            JOIN users u ON p.user_id = u.id
            LEFT JOIN programs pr ON p.program_id = pr.id
            LEFT JOIN users admin ON p.verified_by = admin.id
            WHERE p.id = %s
        """, (payment_id,))
        payment = cur.fetchone()
        
        cur.close()
        
        if not payment:
            return '<p class="text-danger" style="padding: 20px;">Pembayaran tidak ditemukan</p>', 404
        
        # Payment type mapping
        payment_types = {
            'registration': 'Pendaftaran',
            'installment_1': 'Angsuran 1',
            'installment_2': 'Angsuran 2',
            'installment_3': 'Angsuran 3',
            'post_job': 'Setelah Job',
            'certification': 'Sertifikasi'
        }
        
        # Status badge mapping
        status_badges = {
            'pending': '<span class="badge bg-warning">Pending</span>',
            'verified': '<span class="badge bg-success">Verified</span>',
            'rejected': '<span class="badge bg-danger">Rejected</span>'
        }
        
        # Build HTML response
        html = f"""
        <div style="padding: 10px;">
            <table style="width: 100%; border-collapse: collapse;">
                <tr style="border-bottom: 1px solid #e5e7eb;">
                    <td style="padding: 12px 8px; font-weight: 600; width: 40%;">Nama:</td>
                    <td style="padding: 12px 8px;">{payment.get('full_name', '-')}</td>
                </tr>
                <tr style="border-bottom: 1px solid #e5e7eb;">
                    <td style="padding: 12px 8px; font-weight: 600;">Email:</td>
                    <td style="padding: 12px 8px;">{payment.get('email', '-')}</td>
                </tr>
                <tr style="border-bottom: 1px solid #e5e7eb;">
                    <td style="padding: 12px 8px; font-weight: 600;">Telepon:</td>
                    <td style="padding: 12px 8px;">{payment.get('phone', '-')}</td>
                </tr>
                <tr style="border-bottom: 1px solid #e5e7eb;">
                    <td style="padding: 12px 8px; font-weight: 600;">Jenis Kelas:</td>
                    <td style="padding: 12px 8px;"><span class="badge bg-secondary">{payment.get('class_type', '-')}</span></td>
                </tr>
                <tr style="border-bottom: 1px solid #e5e7eb;">
                    <td style="padding: 12px 8px; font-weight: 600;">Jenis Pembayaran:</td>
                    <td style="padding: 12px 8px;">{payment_types.get(payment.get('payment_type'), payment.get('payment_type', '-'))}</td>
                </tr>
                <tr style="border-bottom: 1px solid #e5e7eb;">
                    <td style="padding: 12px 8px; font-weight: 600;">Jumlah:</td>
                    <td style="padding: 12px 8px;"><strong style="font-size: 18px; color: #e11d48;">Rp {payment.get('amount', 0):,.0f}</strong></td>
                </tr>
                <tr style="border-bottom: 1px solid #e5e7eb;">
                    <td style="padding: 12px 8px; font-weight: 600;">Status:</td>
                    <td style="padding: 12px 8px;">{status_badges.get(payment.get('status'), payment.get('status', '-'))}</td>
                </tr>
                <tr style="border-bottom: 1px solid #e5e7eb;">
                    <td style="padding: 12px 8px; font-weight: 600;">Tanggal Bayar:</td>
                    <td style="padding: 12px 8px;">{payment.get('payment_date').strftime('%d/%m/%Y %H:%M') if payment.get('payment_date') else '-'}</td>
                </tr>
        """
        
        if payment.get('rejection_reason'):
            html += f"""
                <tr style="border-bottom: 1px solid #e5e7eb; background: #fef2f2;">
                    <td style="padding: 12px 8px; font-weight: 600; color: #ef4444;">Alasan Penolakan:</td>
                    <td style="padding: 12px 8px; color: #ef4444;">{payment['rejection_reason']}</td>
                </tr>
            """
        
        if payment.get('verified_at'):
            html += f"""
                <tr style="border-bottom: 1px solid #e5e7eb;">
                    <td style="padding: 12px 8px; font-weight: 600;">Waktu Verifikasi:</td>
                    <td style="padding: 12px 8px;">{payment['verified_at'].strftime('%d/%m/%Y %H:%M')}</td>
                </tr>
            """
            
        if payment.get('verified_by_name'):
            html += f"""
                <tr style="border-bottom: 1px solid #e5e7eb;">
                    <td style="padding: 12px 8px; font-weight: 600;">Diverifikasi oleh:</td>
                    <td style="padding: 12px 8px;">{payment['verified_by_name']}</td>
                </tr>
            """
        
        if payment.get('proof_file'):
            proof_url = url_for('static', filename='uploads/' + payment['proof_file'])
            html += f"""
                <tr>
                    <td style="padding: 12px 8px; font-weight: 600;">Bukti Pembayaran:</td>
                    <td style="padding: 12px 8px;">
                        <a href="{proof_url}" target="_blank" class="btn btn-outline-primary btn-sm">
                            <i class="fas fa-image me-1"></i>Lihat Bukti
                        </a>
                    </td>
                </tr>
            """
        
        html += """
            </table>
        </div>
        """
        
        return html, 200
        
    except Exception as e:
        print(f"Error loading payment detail: {str(e)}")
        return f'<p style="color: #ef4444; padding: 20px;">Terjadi kesalahan: {str(e)}</p>', 500

