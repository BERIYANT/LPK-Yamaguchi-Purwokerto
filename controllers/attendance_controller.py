
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from utils.authentication import login_required, teacher_required, admin_required
from models.attendance_model import AttendanceModel
from models.class_model import ClassModel
from datetime import datetime, date

attendance_bp = Blueprint('attendance', __name__)

# Manual attendance by teacher
@attendance_bp.route('/teacher/attendance/manual/<int:session_id>', methods=['POST'])
@login_required
@teacher_required
def teacher_manual_attendance(session_id):
    """Guru menandai siswa hadir secara manual"""
    att_session = AttendanceModel.get_session_by_id(session_id)
    if not att_session:
        flash('Sesi absensi tidak ditemukan!', 'danger')
        return redirect(url_for('attendance.teacher_attendance_list'))
    if att_session['teacher_id'] != session['user_id']:
        flash('Anda tidak memiliki akses!', 'danger')
        return redirect(url_for('attendance.teacher_attendance_list'))
    student_id = request.form.get('student_id')
    if not student_id:
        flash('ID siswa tidak valid!', 'danger')
        return redirect(url_for('attendance.teacher_attendance_report', session_id=session_id))
    record_id = AttendanceModel.record_attendance(session_id, student_id)
    if record_id:
        flash('Kehadiran siswa berhasil dicatat secara manual.', 'success')
    else:
        flash('Siswa sudah tercatat hadir.', 'info')
    return redirect(url_for('attendance.teacher_attendance_report', session_id=session_id))

# ==================== TEACHER ROUTES ====================

@attendance_bp.route('/teacher/attendance/create', methods=['GET', 'POST'])
@login_required
@teacher_required
def teacher_create_attendance():
    """Teacher creates a new attendance session"""
    if request.method == 'POST':
        class_id = request.form.get('class_id')
        date_str = request.form.get('date')
        description = request.form.get('description', '')
        
        if not class_id or not date_str:
            flash('Kelas dan tanggal harus diisi!', 'danger')
            return redirect(url_for('attendance.teacher_create_attendance'))
        
        try:
            # Create attendance session
            session_id, token = AttendanceModel.create_attendance_session(
                class_id, 
                session['user_id'], 
                date_str,
                description
            )
            
            flash('Sesi absensi berhasil dibuat!', 'success')
            return redirect(url_for('attendance.teacher_view_barcode', session_id=session_id))
            
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('attendance.teacher_create_attendance'))
    
    # GET - show form
    classes = ClassModel.get_classes_by_teacher(session['user_id'])
    return render_template('teacher/create_attendance.html', 
                          classes=classes, 
                          today=date.today().isoformat())

@attendance_bp.route('/teacher/attendance/barcode/<int:session_id>')
@login_required
@teacher_required
def teacher_view_barcode(session_id):
    """Teacher views the generated barcode"""
    att_session = AttendanceModel.get_session_by_id(session_id)
    
    if not att_session:
        flash('Sesi absensi tidak ditemukan!', 'danger')
        return redirect(url_for('attendance.teacher_attendance_list'))
    
    # Check if teacher owns this session
    if att_session['teacher_id'] != session['user_id']:
        flash('Anda tidak memiliki akses!', 'danger')
        return redirect(url_for('attendance.teacher_attendance_list'))
    
    # Generate barcode image
    base_url = request.host_url.rstrip('/')
    barcode_img = AttendanceModel.generate_barcode_image(att_session['token'], base_url)
    
    return render_template('teacher/view_barcode.html', 
                          session=att_session, 
                          barcode_img=barcode_img)

@attendance_bp.route('/teacher/attendance/refresh-barcode/<int:session_id>')
@login_required
@teacher_required
def refresh_barcode(session_id):
    """Refresh the barcode token via AJAX"""
    att_session = AttendanceModel.get_session_by_id(session_id)
    
    if not att_session:
        return jsonify({'error': 'Session not found'}), 404
    
    # Check if teacher owns this session
    if att_session['teacher_id'] != session['user_id']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Refresh the token
    new_token, expires_at = AttendanceModel.refresh_token(session_id)
    
    # Generate new barcode
    base_url = request.host_url.rstrip('/')
    barcode_img = AttendanceModel.generate_barcode_image(new_token, base_url)
    
    # Return JSON response
    return jsonify({
        'token': new_token,
        'expires_at': expires_at.isoformat() if expires_at else None,
        'barcode_img': barcode_img,
        'attendance_link': f"{base_url}/student/attendance/scan?token={new_token}"
    })

@attendance_bp.route('/teacher/attendance/list')
@login_required
@teacher_required
def teacher_attendance_list():
    """Teacher views all their attendance sessions"""
    date_filter = request.args.get('date')
    sessions = AttendanceModel.get_sessions_by_teacher(session['user_id'], date_filter)
    
    return render_template('teacher/attendance_list.html', 
                          sessions=sessions, 
                          date_filter=date_filter,
                          today=date.today().isoformat())

@attendance_bp.route('/teacher/attendance/report/<int:session_id>')
@login_required
@teacher_required
def teacher_attendance_report(session_id):
    """Teacher views detailed attendance report"""
    att_session = AttendanceModel.get_session_by_id(session_id)
    
    if not att_session:
        flash('Sesi absensi tidak ditemukan!', 'danger')
        return redirect(url_for('attendance.teacher_attendance_list'))
    
    # Check if teacher owns this session
    if att_session['teacher_id'] != session['user_id']:
        flash('Anda tidak memiliki akses!', 'danger')
        return redirect(url_for('attendance.teacher_attendance_list'))
    
    summary = AttendanceModel.get_attendance_summary(session_id)
    
    return render_template('teacher/attendance_report.html', summary=summary)

@attendance_bp.route('/teacher/attendance/deactivate/<int:session_id>', methods=['POST'])
@login_required
@teacher_required
def teacher_deactivate_session(session_id):
    """Teacher deactivates an attendance session"""
    att_session = AttendanceModel.get_session_by_id(session_id)
    
    if not att_session:
        flash('Sesi absensi tidak ditemukan!', 'danger')
        return redirect(url_for('attendance.teacher_attendance_list'))
    
    # Check if teacher owns this session
    if att_session['teacher_id'] != session['user_id']:
        flash('Anda tidak memiliki akses!', 'danger')
        return redirect(url_for('attendance.teacher_attendance_list'))
    
    AttendanceModel.deactivate_session(session_id)
    flash('Sesi absensi telah dinonaktifkan!', 'success')
    
    return redirect(url_for('attendance.teacher_attendance_list'))

# ==================== STUDENT ROUTES ====================

@attendance_bp.route('/student/attendance/scan')
@login_required
def student_scan_attendance():
    """Student scans barcode to mark attendance"""
    token = request.args.get('token')
    
    if not token:
        return render_template('student/scan_attendance.html')
    
    # Get session by token
    att_session = AttendanceModel.get_session_by_token(token)
    
    if not att_session:
        flash('Kode absensi tidak valid!', 'danger')
        return redirect(url_for('attendance.student_scan_attendance'))
    
    # Check if session is still active
    if not att_session['is_active']:
        flash('Sesi absensi sudah tidak aktif!', 'warning')
        return redirect(url_for('attendance.student_scan_attendance'))
    
    # Check if session has expired
    if AttendanceModel.is_session_expired(att_session['id']):
        flash('Waktu absensi telah berakhir (batas 5 menit)!', 'warning')
        return redirect(url_for('attendance.student_scan_attendance'))
    
    # Record attendance
    record_id = AttendanceModel.record_attendance(att_session['id'], session['user_id'])
    
    if record_id:
        flash(f'Absensi berhasil dicatat untuk kelas {att_session["class_name"]}!', 'success')
    else:
        flash('Anda sudah melakukan absensi untuk sesi ini!', 'info')
    
    return redirect(url_for('attendance.student_attendance_history'))

@attendance_bp.route('/student/attendance/history')
@login_required
def student_attendance_history():
    """Student views their attendance history"""
    history = AttendanceModel.get_student_attendance_history(session['user_id'])
    return render_template('student/attendance_history.html', history=history)

# ==================== ADMIN ROUTES ====================

@attendance_bp.route('/admin/attendance/report')
@login_required
@admin_required
def admin_attendance_report():
    """Admin views all attendance sessions"""
    date_filter = request.args.get('date')
    sessions = AttendanceModel.get_all_sessions(date_filter)
    
    return render_template('admin/attendance_report.html', 
                          sessions=sessions, 
                          date_filter=date_filter,
                          today=date.today().isoformat())

@attendance_bp.route('/admin/attendance/detail/<int:session_id>')
@login_required
@admin_required
def admin_attendance_detail(session_id):
    """Admin views detailed attendance for a specific session"""
    summary = AttendanceModel.get_attendance_summary(session_id)
    
    if not summary:
        flash('Sesi absensi tidak ditemukan!', 'danger')
        return redirect(url_for('attendance.admin_attendance_report'))
    
    return render_template('admin/attendance_detail.html', summary=summary)
