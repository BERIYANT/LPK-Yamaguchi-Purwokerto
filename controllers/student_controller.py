from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
from utils.authentication import login_required
from utils.database import get_db
from models.material_model import MaterialModel
from models.quiz_model import QuizModel, QuizQuestionModel
from models.assignment_model import AssignmentModel, AssignmentSubmissionModel
from models.certificate_model import CertificateModel
from utils.file_handler import allowed_file, save_uploaded_file
import os
from datetime import datetime, timedelta

student_bp = Blueprint('student', __name__)

def _normalize_img_path(p):
    # Ensure filename is prefixed with uploads/ for your download_file route
    if not p:
        return None
    return p if ('/' in p and p.split('/', 1)[0] == 'uploads') else f"uploads/{p}"

@student_bp.route('/dashboard')
@login_required
def dashboard():
    if g.user.get('role') != 'student':
        flash("Akses ditolak.")
        # FIX: endpoint 'main.dashboard' invalid, redirect to admin dashboard
        return redirect(url_for('admin.dashboard'))
    
    db = get_db()
    cur = db.cursor(dictionary=True)
    
    # Get student's class
    cur.execute("""
        SELECT class_id FROM enrollments 
        WHERE user_id = %s LIMIT 1
    """, (g.user['id'],))
    enrollment = cur.fetchone()
    
    materials = []
    quizzes = []
    tasks = []
    
    if enrollment:
        class_id = enrollment['class_id']
        
        # Get materials
        materials = MaterialModel.get_by_class(class_id)
        
        # Get quizzes with completion status, attempts_used, and total_questions
        cur.execute("""
            SELECT q.*,
                (SELECT COUNT(*) FROM quiz_scores WHERE quiz_id = q.id AND student_id = %s) AS is_completed,
                (SELECT COUNT(*) FROM quiz_scores WHERE quiz_id = q.id AND student_id = %s) AS attempts_used,
                (SELECT COUNT(*) FROM quiz_questions WHERE quiz_id = q.id) AS total_questions
            FROM quizzes q
            WHERE q.class_id = %s
            ORDER BY q.created_at DESC
        """, (g.user['id'], g.user['id'], class_id))
        quizzes = cur.fetchall()

        now = datetime.now()
        for q in quizzes:
            limit = q.get('attempt_limit')
            used = q.get('attempts_used') or 0
            total_q = q.get('total_questions') or 0
            past_due = bool(q.get('due_at') and now > q['due_at'])
            if limit is not None:
                try:
                    limit = int(limit)
                except:
                    limit = None
            remaining = (limit - used) if (limit is not None) else None
            # Clamp remaining attempts to non-negative number
            if isinstance(remaining, int) and remaining < 0:
                remaining = 0
            q['remaining_attempts'] = remaining if remaining is not None else '∞'
            # Only allow take if before due, attempts not exhausted, and quiz has questions
            q['can_take'] = (not past_due) and ((limit is None) or (used < limit)) and (total_q > 0)

        # Get tasks with submission status and score
        cur.execute("""
            SELECT t.*,
                ts.id as submission_id,
                ts.score,
                ts.submitted_at,
                ts.graded_at
            FROM tasks t
            LEFT JOIN task_submissions ts ON t.id = ts.task_id AND ts.student_id = %s
            WHERE t.class_id = %s
            ORDER BY t.created_at DESC
        """, (g.user['id'], class_id))
        tasks = cur.fetchall()
    
    cur.close()
    
    return render_template('student/dashboard.html', 
                           materials=materials, 
                           quizzes=quizzes, 
                           tasks=tasks)

@student_bp.route('/material/<int:material_id>')
@login_required
def view_material(material_id):
    if g.user.get('role') != 'student':
        flash("Akses ditolak.")
        # FIX
        return redirect(url_for('admin.dashboard'))
    
    material = MaterialModel.get_by_id(material_id)
    if not material:
        flash("Materi tidak ditemukan.")
        return redirect(url_for('student.dashboard'))
    
    return render_template('student/view_material.html', material=material)

@student_bp.route('/quiz/<int:quiz_id>')
@login_required
def view_quiz(quiz_id):
    if g.user.get('role') != 'student':
        flash("Akses ditolak.")
        # FIX
        return redirect(url_for('admin.dashboard'))
    
    db = get_db()
    cur = db.cursor(dictionary=True)
    
    # Check if quiz exists and get details
    cur.execute("SELECT * FROM quizzes WHERE id=%s", (quiz_id,))
    quiz = cur.fetchone()
    if not quiz:
        flash("Kuis tidak ditemukan.")
        return redirect(url_for('student.dashboard'))

    # Get questions
    cur.execute("SELECT * FROM quiz_questions WHERE quiz_id=%s ORDER BY id", (quiz_id,))
    questions = cur.fetchall()

    # Attempts used
    cur.execute("SELECT COUNT(*) AS cnt FROM quiz_scores WHERE quiz_id=%s AND student_id=%s", (quiz_id, g.user['id']))
    attempts_used = cur.fetchone()['cnt']

    # Existing score (latest)
    cur.execute("SELECT * FROM quiz_scores WHERE quiz_id=%s AND student_id=%s ORDER BY graded_at DESC LIMIT 1", (quiz_id, g.user['id']))
    existing_score = cur.fetchone()

    cur.close()
    return render_template('student/view_quiz.html',
                           quiz=quiz,
                           questions=questions,
                           existing_score=existing_score,
                           attempts_used=attempts_used,
                           now=datetime.now())

@student_bp.route('/quiz/<int:quiz_id>/take', methods=['GET', 'POST'])
@login_required
def take_quiz(quiz_id):
    if g.user.get('role') != 'student':
        flash("Akses ditolak.")
        # FIX
        return redirect(url_for('admin.dashboard'))
    
    db = get_db()
    cur = db.cursor(dictionary=True)

    # Load quiz settings
    cur.execute("SELECT * FROM quizzes WHERE id=%s", (quiz_id,))
    quiz = cur.fetchone()
    if not quiz:
        flash("Kuis tidak ditemukan.")
        cur.close()
        return redirect(url_for('student.dashboard'))

    # Enforce due date
    if quiz.get('due_at') and datetime.now() > quiz['due_at']:
        cur.close()
        flash("Kuis sudah melewati batas waktu.")
        return redirect(url_for('student.view_quiz', quiz_id=quiz_id))

    # Enforce attempt limit
    cur.execute("SELECT COUNT(*) AS cnt FROM quiz_scores WHERE quiz_id=%s AND student_id=%s", (quiz_id, g.user['id']))
    attempts_used = cur.fetchone()['cnt']
    if quiz.get('attempt_limit') and attempts_used >= int(quiz['attempt_limit']):
        cur.close()
        flash("Anda telah mencapai batas jumlah percobaan untuk kuis ini.")
        return redirect(url_for('student.view_quiz', quiz_id=quiz_id))

    # Legacy single-attempt behavior if no attempt_limit provided
    cur.execute("SELECT * FROM quiz_scores WHERE quiz_id=%s AND student_id=%s", (quiz_id, g.user['id']))
    existing_score = cur.fetchone()
    if existing_score and not quiz.get('attempt_limit'):
        flash("Anda sudah mengerjakan kuis ini.")
        cur.close()
        return redirect(url_for('student.quiz_result', quiz_id=quiz_id))

    # Get questions
    cur.execute("SELECT * FROM quiz_questions WHERE quiz_id=%s ORDER BY id", (quiz_id,))
    questions = cur.fetchall()
    for q in questions:
        q['image_path'] = _normalize_img_path(q.get('image_path'))
        q['option_a_img'] = _normalize_img_path(q.get('option_a_img'))
        q['option_b_img'] = _normalize_img_path(q.get('option_b_img'))
        q['option_c_img'] = _normalize_img_path(q.get('option_c_img'))
        q['option_d_img'] = _normalize_img_path(q.get('option_d_img'))
        q['option_e_img'] = _normalize_img_path(q.get('option_e_img'))
    
    if not questions:
        flash("Kuis ini belum memiliki pertanyaan.")
        cur.close()
        return redirect(url_for('student.dashboard'))
    
    # Determine remaining attempts for UI
    remaining_attempts = '∞'
    if quiz.get('attempt_limit'):
        try:
            remaining_attempts = max(0, int(quiz['attempt_limit']) - attempts_used)
        except:
            remaining_attempts = '∞'

    # Initialize attempt start in session (for duration enforcement)
    key = f"quiz_start_{quiz_id}"
    if request.method == 'GET':
        if quiz.get('duration_minutes'):
            if not session.get(key):
                session[key] = datetime.now().isoformat()
        cur.close()
        return render_template('student/take_quiz.html',
                               questions=questions,
                               quiz_id=quiz_id,
                               quiz=quiz,
                               remaining_attempts=remaining_attempts)

    # POST: enforce duration if set
    start_iso = session.get(key)
    if quiz.get('duration_minutes') and start_iso:
        try:
            start_dt = datetime.fromisoformat(start_iso)
            if datetime.now() > start_dt + timedelta(minutes=int(quiz['duration_minutes'])):
                cur.close()
                # Clear start time for next attempt
                session.pop(key, None)
                flash("Waktu pengerjaan kuis telah habis. Silakan mulai attempt baru jika masih tersedia.")
                return redirect(url_for('student.view_quiz', quiz_id=quiz_id))
        except:
            pass

    if request.method == 'POST':
        total = len(questions)
        correct_count = 0
        for question in questions:
            field = f"q{question['id']}"
            answer = request.form.get(field, '').strip().lower()
            is_correct = bool(answer and answer == question['correct_option'].lower())
            if is_correct:
                correct_count += 1
            cur.execute("""
                INSERT INTO quiz_answers (quiz_id, question_id, student_id, selected_option, is_correct, answered_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (quiz_id, question['id'], g.user['id'], answer, is_correct, datetime.now()))
        
        score = round((correct_count / total) * 100, 2) if total > 0 else 0
        cur.execute("""
            INSERT INTO quiz_scores (quiz_id, student_id, score, graded_at)
            VALUES (%s, %s, %s, %s)
        """, (quiz_id, g.user['id'], score, datetime.now()))
        
        db.commit()
        cur.close()
        # Clear start timestamp after submission
        session.pop(key, None)
        flash("Kuis selesai! Nilai kamu telah dihitung otomatis.")
        return redirect(url_for('student.quiz_result', quiz_id=quiz_id))
    
    cur.close()
    return render_template('student/take_quiz.html', questions=questions, quiz_id=quiz_id)

@student_bp.route('/quiz/<int:quiz_id>/result')
@login_required
def quiz_result(quiz_id):
    if g.user.get('role') != 'student':
        flash("Akses ditolak.")
        # FIX
        return redirect(url_for('admin.dashboard'))
    
    db = get_db()
    cur = db.cursor(dictionary=True)
    
    # Get latest score
    cur.execute("""
        SELECT * FROM quiz_scores
        WHERE quiz_id=%s AND student_id=%s
        ORDER BY graded_at DESC LIMIT 1
    """, (quiz_id, g.user['id']))
    score = cur.fetchone()
    
    if not score:
        flash("Anda belum mengerjakan kuis ini.")
        return redirect(url_for('student.view_quiz', quiz_id=quiz_id))
    
    # Get quiz details
    cur.execute("SELECT title FROM quizzes WHERE id=%s", (quiz_id,))
    quiz = cur.fetchone()
    
    # Get answers with questions (include image columns)
    cur.execute("""
        SELECT qq.question, qq.image_path,
               qq.option_a, qq.option_b, qq.option_c, qq.option_d, qq.option_e,
               qq.option_a_img, qq.option_b_img, qq.option_c_img, qq.option_d_img, qq.option_e_img,
               qq.correct_option, qa.selected_option, qa.is_correct
        FROM quiz_questions qq
        LEFT JOIN quiz_answers qa ON qq.id = qa.question_id AND qa.student_id = %s
        WHERE qq.quiz_id = %s
        ORDER BY qq.id
    """, (g.user['id'], quiz_id))
    answers = cur.fetchall()
    # Normalize image paths for rendering in result template
    for a in answers:
        a['image_path'] = _normalize_img_path(a.get('image_path'))
        a['option_a_img'] = _normalize_img_path(a.get('option_a_img'))
        a['option_b_img'] = _normalize_img_path(a.get('option_b_img'))
        a['option_c_img'] = _normalize_img_path(a.get('option_c_img'))
        a['option_d_img'] = _normalize_img_path(a.get('option_d_img'))
        a['option_e_img'] = _normalize_img_path(a.get('option_e_img'))
    
    cur.close()
    
    return render_template('student/quiz_result.html', 
                         quiz=quiz, 
                         score=score, 
                         answers=answers)

@student_bp.route('/my-quiz-history')
@login_required
def my_quiz_history():
    if g.user.get('role') != 'student':
        flash("Halaman ini hanya untuk siswa.")
        # FIX
        return redirect(url_for('admin.dashboard'))
    
    db = get_db()
    cur = db.cursor(dictionary=True)
    
    try:
        # Get all quizzes taken by student
        cur.execute("""
            SELECT 
                q.id as quiz_id,
                q.title as quiz_title,
                qs.id as score_id,
                qs.score,
                qs.graded_at,
                c.name as class_name,
                (SELECT COUNT(*) FROM quiz_questions WHERE quiz_id = q.id) as total_questions
            FROM quiz_scores qs
            JOIN quizzes q ON qs.quiz_id = q.id
            LEFT JOIN classes c ON q.class_id = c.id
            WHERE qs.student_id = %s
            ORDER BY qs.graded_at DESC
        """, (g.user['id'],))
        quiz_history = cur.fetchall()
        
        # Calculate statistics
        if quiz_history:
            scores = [h['score'] for h in quiz_history]
            avg_score = sum(scores) / len(scores)
            highest_score = max(scores)
            lowest_score = min(scores)
            total_quiz = len(quiz_history)
        else:
            avg_score = 0
            highest_score = 0
            lowest_score = 0
            total_quiz = 0
        
        stats = {
            'total_quiz': total_quiz,
            'avg_score': round(avg_score, 1),
            'highest_score': highest_score,
            'lowest_score': lowest_score
        }
        
        return render_template('student/quiz_history.html', 
                             quiz_history=quiz_history, 
                             stats=stats)
    
    except Exception as e:
        flash(f"Terjadi kesalahan: {str(e)}")
        return redirect(url_for('student.dashboard'))
    finally:
        cur.close()

@student_bp.route('/quiz/<int:quiz_id>/history/<int:score_id>')
@login_required
def view_quiz_history_detail(quiz_id, score_id):
    if g.user.get('role') != 'student':
        flash("Akses ditolak.")
        # FIX
        return redirect(url_for('admin.dashboard'))
    
    db = get_db()
    cur = db.cursor(dictionary=True)
    
    try:
        # Verify score belongs to student
        cur.execute("""
            SELECT 
                qs.id,
                qs.quiz_id,
                qs.score,
                qs.graded_at,
                q.title as quiz_title,
                c.name as class_name
            FROM quiz_scores qs
            JOIN quizzes q ON qs.quiz_id = q.id
            LEFT JOIN classes c ON q.class_id = c.id
            WHERE qs.id = %s 
            AND qs.student_id = %s 
            AND qs.quiz_id = %s
        """, (score_id, g.user['id'], quiz_id))
        score = cur.fetchone()
        
        if not score:
            flash("Data kuis tidak ditemukan atau Anda tidak memiliki akses.")
            return redirect(url_for('student.my_quiz_history'))
        
        # Get detailed answers
        cur.execute("""
            SELECT 
                qq.id as question_id,
                qq.question,
                qq.option_a,
                qq.option_b,
                qq.option_c,
                qq.option_d,
                qq.option_e,
                qq.correct_option,
                COALESCE(qa.selected_option, '') as selected_option,
                COALESCE(qa.is_correct, 0) as is_correct
            FROM quiz_questions qq
            LEFT JOIN quiz_answers qa ON qq.id = qa.question_id 
                AND qa.student_id = %s 
                AND qa.quiz_id = %s
            WHERE qq.quiz_id = %s
            ORDER BY qq.id
        """, (g.user['id'], quiz_id, quiz_id))
        answers = cur.fetchall()
        
        # Calculate answer statistics
        total_questions = len(answers)
        correct_answers = sum(1 for a in answers if a.get('is_correct'))
        wrong_answers = total_questions - correct_answers
        
        answer_stats = {
            'total': total_questions,
            'correct': correct_answers,
            'wrong': wrong_answers
        }
        
        return render_template('student/quiz_history_detail.html', 
                             score=score, 
                             answers=answers, 
                             answer_stats=answer_stats)
    
    except Exception as e:
        flash(f"Terjadi kesalahan: {str(e)}")
        return redirect(url_for('student.my_quiz_history'))
    finally:
        cur.close()

@student_bp.route('/assignment/<int:task_id>')
@login_required
def view_assignment(task_id):
    if g.user.get('role') != 'student':
        flash("Akses ditolak.")
        # FIX: this line caused the BuildError per traceback
        return redirect(url_for('admin.dashboard'))
    
    task = AssignmentModel.get_by_id(task_id)
    if not task:
        flash("Tugas tidak ditemukan.")
        return redirect(url_for('student.dashboard'))
    
    # Check if student has submitted
    submission = AssignmentSubmissionModel.get_by_task_and_student(task_id, g.user['id'])
    
    return render_template('student/view_assignment.html', 
                         task=task, 
                         submission=submission)

@student_bp.route('/assignment/<int:task_id>/upload', methods=['GET', 'POST'])
@login_required
def upload_assignment(task_id):
    if g.user.get('role') != 'student':
        flash("Akses ditolak.")
        # FIX
        return redirect(url_for('admin.dashboard'))
    
    task = AssignmentModel.get_by_id(task_id)
    if not task:
        flash("Tugas tidak ditemukan.")
        return redirect(url_for('student.dashboard'))
    
    # Check existing submission
    existing_submission = AssignmentSubmissionModel.get_by_task_and_student(task_id, g.user['id'])
    
    if request.method == 'POST':
        file = request.files.get('file')
        if file and file.filename:
            if not allowed_file(file.filename):
                flash('Format file tidak diizinkan.')
                return redirect(url_for('student.upload_assignment', task_id=task_id))
            
            try:
                safe_name = f"{g.user['username']}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
                file_path = save_uploaded_file(file, f"submission_{task_id}")
                
                if existing_submission:
                    # Update existing submission
                    from utils.database import get_db
                    db = get_db()
                    cur = db.cursor()
                    
                    # Delete old file if exists
                    if existing_submission.get('file_path'):
                        old_file_path = existing_submission['file_path']
                        old_paths = [
                            os.path.join('static/uploads', old_file_path),
                            os.path.join('static/uploads', old_file_path.replace('uploads/', ''))
                        ]
                        for old_file in old_paths:
                            if os.path.exists(old_file):
                                try:
                                    os.remove(old_file)
                                    break
                                except:
                                    pass
                    
                    # Update submission
                    cur.execute("""
                        UPDATE task_submissions 
                        SET file_path=%s, submitted_at=%s, score=NULL, feedback=NULL, graded_by=NULL, graded_at=NULL
                        WHERE id=%s
                    """, (file_path, datetime.now(), existing_submission['id']))
                    db.commit()
                    cur.close()
                    
                    flash("File tugas berhasil diperbarui. Nilai sebelumnya telah dihapus.")
                else:
                    # Create new submission
                    AssignmentSubmissionModel.create(task_id, g.user['id'], file_path)
                    flash("Tugas berhasil diupload.")
                
                return redirect(url_for('student.my_task_scores'))
            except Exception as e:
                flash(f'Gagal mengupload file: {str(e)}')
        else:
            flash("Pilih file yang ingin diupload.")
    
    return render_template('student/upload_assignment.html', 
                         task=task, 
                         existing_submission=existing_submission)

@student_bp.route('/submission/<int:submission_id>/delete')
@login_required
def delete_submission(submission_id):
    if g.user.get('role') != 'student':
        flash("Akses ditolak.")
        # FIX
        return redirect(url_for('admin.dashboard'))
    
    db = get_db()
    cur = db.cursor(dictionary=True)
    
    # Verify submission belongs to student
    cur.execute("""
        SELECT * FROM task_submissions 
        WHERE id=%s AND student_id=%s
    """, (submission_id, g.user['id']))
    submission = cur.fetchone()
    
    if not submission:
        flash("Submission tidak ditemukan atau Anda tidak memiliki akses.")
        return redirect(url_for('student.my_task_scores'))
    
    # Delete physical file
    if submission.get('file_path'):
        file_path = submission['file_path']
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
    
    # Delete from database
    cur.execute("DELETE FROM task_submissions WHERE id=%s", (submission_id,))
    db.commit()
    cur.close()
    
    flash("File tugas berhasil dihapus.")
    return redirect(url_for('student.upload_assignment', task_id=submission['task_id']))

@student_bp.route('/my-task-scores')
@login_required
def my_task_scores():
    if g.user.get('role') != 'student':
        flash("Halaman ini hanya untuk siswa.")
        # FIX
        return redirect(url_for('admin.dashboard'))
    
    submissions = AssignmentSubmissionModel.get_student_submissions(g.user['id'])
    return render_template('student/task_scores.html', submissions=submissions)

@student_bp.route('/my-certificates')
@login_required
def my_certificates():
    if g.user.get('role') != 'student':
        flash("Halaman ini hanya untuk siswa.")
        # FIX
        return redirect(url_for('admin.dashboard'))
    
    certificates = CertificateModel.get_by_student(g.user['id'])
    # Inject proper URLs for student views and downloads
    try:
        from flask import current_app
        import os
        app_root = current_app.root_path
        for cert in certificates or []:
            # prefer student detail route
            cert['detail_url'] = url_for('student.view_certificate', certificate_id=cert['id'])
            # use certificate download endpoint
            cert['download_url'] = url_for('certificate.download_certificate', certificate_id=cert['id'])
            # Optional legacy static URL if exists
            fp = cert.get('file_path') or ''
            rel = fp[8:] if fp.startswith('uploads/') else fp
            candidates = [
                os.path.join(app_root, 'static', 'uploads', rel),
                os.path.join(app_root, 'static', rel),
            ]
            existing = None
            for abs_path in candidates:
                if os.path.exists(abs_path) and os.path.isfile(abs_path):
                    if abs_path.endswith(os.path.join('static', 'uploads', rel)):
                        existing = f"uploads/{rel}"
                    else:
                        existing = rel
                    break
            cert['file_url'] = url_for('static', filename=existing) if existing else None
    except Exception:
        pass

    return render_template('student/my_certificates.html', certificates=certificates)

@student_bp.route('/certificate/<int:certificate_id>')
@login_required
def view_certificate(certificate_id):
    if g.user.get('role') != 'student':
        flash("Akses ditolak.")
        return redirect(url_for('admin.dashboard'))
    cert = CertificateModel.get_by_id(certificate_id)
    if not cert:
        flash("Sertifikat tidak ditemukan.")
        return redirect(url_for('student.my_certificates'))
    return render_template('student/view_certificate.html', cert=cert)