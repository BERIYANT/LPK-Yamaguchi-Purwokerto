from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_file, g
from utils.authentication import login_required
from models.assignment_model import AssignmentModel
import os

assignment_bp = Blueprint('assignment', __name__)

@assignment_bp.route('/assignment/<int:task_id>/download')
@login_required
def download_assignment_file(task_id):
    task = AssignmentModel.get_by_id(task_id)
    if not task:
        flash("Tugas tidak ditemukan.")
        # FIX: wrong endpoint
        return redirect(url_for('admin.dashboard'))
    
    if not task.get('file_path'):
        flash("Tugas ini tidak memiliki file.")
        return redirect(url_for('student.view_assignment', task_id=task_id))
    
    try:
        file_path = task['file_path']
        # Normalize path
        if file_path.startswith('uploads/'):
            file_path = file_path[8:]
        
        # Try different possible paths
        possible_paths = [
            os.path.join('static/uploads', file_path),
            os.path.join('static/uploads', file_path.replace('uploads/', '')),
            os.path.join('static', file_path)
        ]
        
        for full_path in possible_paths:
            if os.path.exists(full_path):
                # Get file extension for download name
                file_ext = file_path.split('.')[-1] if '.' in file_path else 'file'
                download_name = f"{task['title']}.{file_ext}"
                
                return send_file(
                    full_path,
                    as_attachment=True,
                    download_name=download_name
                )
        
        flash("File tidak ditemukan di server.")
        return redirect(url_for('student.view_assignment', task_id=task_id))
        
    except Exception as e:
        flash(f"Error: {str(e)}")
        return redirect(url_for('student.view_assignment', task_id=task_id))

@assignment_bp.route('/submission/<int:submission_id>/download')
@login_required
def download_submission_file(submission_id):
    from utils.database import get_db
    db = get_db()
    cur = db.cursor(dictionary=True)
    
    cur.execute("""
        SELECT ts.*, u.username, t.title as task_title
        FROM task_submissions ts
        JOIN users u ON ts.student_id = u.id
        JOIN tasks t ON ts.task_id = t.id
        WHERE ts.id = %s
    """, (submission_id,))
    submission = cur.fetchone()
    cur.close()
    
    if not submission:
        flash("Submission tidak ditemukan.")
        return redirect(url_for('student.my_task_scores'))
    
    # Resolve user role and id safely
    user_obj = getattr(g, 'user', None)
    user_role = (user_obj.get('role') if isinstance(user_obj, dict) else None) or session.get('role')
    user_id_val = (user_obj.get('id') if isinstance(user_obj, dict) else None) or session.get('user_id')
    try:
        user_id = int(user_id_val) if user_id_val is not None else None
    except:
        user_id = None
    
    # Allow only owner if student; teachers/admins bypass
    if user_role == 'student' and user_id is not None and int(submission['student_id']) != user_id:
        flash("Anda tidak memiliki akses ke file ini.")
        return redirect(url_for('student.my_task_scores'))
    
    if not submission.get('file_path'):
        flash("Submission ini tidak memiliki file.")
        return redirect(url_for('student.my_task_scores'))
    
    try:
        file_path = submission['file_path']
        # Normalize path
        if file_path.startswith('uploads/'):
            file_path = file_path[8:]
        
        # Try different possible paths
        possible_paths = [
            os.path.join('static/uploads', file_path),
            os.path.join('static/uploads', file_path.replace('uploads/', '')),
            os.path.join('static', file_path)
        ]
        
        for full_path in possible_paths:
            if os.path.exists(full_path):
                # Get file extension for download name
                file_ext = file_path.split('.')[-1] if '.' in file_path else 'file'
                download_name = f"{submission['task_title']}_{submission['username']}.{file_ext}"
                
                return send_file(
                    full_path,
                    as_attachment=True,
                    download_name=download_name
                )
        
        flash("File tidak ditemukan di server.")
        return redirect(url_for('student.my_task_scores'))
        
    except Exception as e:
        flash(f"Gagal mengunduh file: {e}")
        return redirect(url_for('student.my_task_scores'))

        