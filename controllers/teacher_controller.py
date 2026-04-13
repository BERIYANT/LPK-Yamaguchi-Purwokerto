from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils.authentication import login_required, teacher_required, class_required
from models.material_model import MaterialModel
from models.quiz_model import QuizModel, QuizQuestionModel
from models.assignment_model import AssignmentModel, AssignmentSubmissionModel
from utils.file_handler import allowed_file, save_uploaded_file
from utils.database import get_db  # FIX: ensure get_db is available globally
import os
from datetime import datetime

teacher_bp = Blueprint('teacher', __name__)

@teacher_bp.route('/dashboard')
@login_required
@teacher_required
def dashboard():
    from models.class_model import ClassModel
    
    classes = ClassModel.get_all()
    selected_class_id = session.get('selected_class_id')
    selected_class = None
    materials = []
    quizzes = []
    tasks = []
    
    if selected_class_id:
        selected_class = ClassModel.get_by_id(selected_class_id)
        materials = MaterialModel.get_by_class(selected_class_id)
        quizzes = QuizModel.get_by_class(selected_class_id)
        tasks = AssignmentModel.get_by_class(selected_class_id)
    
    return render_template('teacher/dashboard.html', 
                         materials=materials, 
                         quizzes=quizzes, 
                         tasks=tasks,
                         classes=classes,
                         selected_class=selected_class)

@teacher_bp.route('/select-class/<int:class_id>')
@login_required
@teacher_required
def select_class(class_id):
    from models.class_model import ClassModel
    
    class_data = ClassModel.get_by_id(class_id)
    if not class_data:
        flash("Kelas tidak ditemukan.")
        return redirect(url_for('teacher.dashboard'))
    
    session['selected_class_id'] = class_id
    flash(f"Kelas '{class_data['name']}' telah dipilih.")
    return redirect(url_for('teacher.dashboard'))

@teacher_bp.route('/clear-class-selection')
@login_required
@teacher_required
def clear_class_selection():
    session.pop('selected_class_id', None)
    flash("Pilihan kelas telah dibatalkan.")
    return redirect(url_for('teacher.dashboard'))

# Materials
@teacher_bp.route('/material/create', methods=['GET', 'POST'])
@login_required
@teacher_required
@class_required
def create_material():
    class_id = session.get('selected_class_id')
    
    if request.method == 'POST':
        title = request.form['title'].strip()
        content = request.form['content']
        file_path = None
        
        # Handle file upload
        file = request.files.get('file')
        if file and file.filename:
            if not allowed_file(file.filename):
                flash('Format file tidak diizinkan.')
                return redirect(url_for('teacher.create_material'))
            
            try:
                safe_name = f"material_{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
                file_path = save_uploaded_file(file, "material")
            except Exception as e:
                flash(f'Gagal mengupload file: {str(e)}')
                return redirect(url_for('teacher.create_material'))
        
        MaterialModel.create(title, content, class_id, session.get('user_id'), file_path)
        flash("Materi berhasil ditambahkan.")
        return redirect(url_for('teacher.dashboard'))
    
    return render_template('teacher/create_material.html', edit=False, material=None)

@teacher_bp.route('/material/<int:material_id>/edit', methods=['GET', 'POST'])
@login_required
@teacher_required
def edit_material(material_id):
    material = MaterialModel.get_by_id(material_id)
    if not material:
        flash("Materi tidak ditemukan.")
        return redirect(url_for('teacher.dashboard'))
    
    # Check if material belongs to teacher
    if material['created_by'] != session.get('user_id'):
        flash("Anda tidak memiliki akses untuk mengedit materi ini.")
        return redirect(url_for('teacher.dashboard'))
    
    if request.method == 'POST':
        title = request.form['title'].strip()
        content = request.form['content']
        file_path = material.get('file_path')
        
        # Handle file upload
        file = request.files.get('file')
        if file and file.filename:
            if not allowed_file(file.filename):
                flash('Format file tidak diizinkan.')
                return redirect(url_for('teacher.edit_material', material_id=material_id))
            
            # Delete old file if exists
            if file_path:
                old_path = os.path.join('static/uploads', file_path)
                if os.path.exists(old_path):
                    try:
                        os.remove(old_path)
                    except:
                        pass
            
            # Upload new file
            try:
                safe_name = f"material_{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
                file_path = save_uploaded_file(file, "material")
            except Exception as e:
                flash(f'Gagal mengupload file: {str(e)}')
                return redirect(url_for('teacher.edit_material', material_id=material_id))
        
        # Option to remove file
        if request.form.get('remove_file') == 'yes' and file_path:
            old_path = os.path.join('static/uploads', file_path)
            if os.path.exists(old_path):
                try:
                    os.remove(old_path)
                except:
                    pass
            file_path = None
        
        MaterialModel.update(material_id, title, content, file_path)
        flash("Materi berhasil diperbarui.")
        return redirect(url_for('teacher.dashboard'))
    
    return render_template('teacher/create_material.html', edit=True, material=material)

@teacher_bp.route('/material/<int:material_id>/delete')
@login_required
@teacher_required
def delete_material(material_id):
    material = MaterialModel.get_by_id(material_id)
    if not material:
        flash("Materi tidak ditemukan.")
        return redirect(url_for('teacher.dashboard'))
    
    # Check if material belongs to teacher
    if material['created_by'] != session.get('user_id'):
        flash("Anda tidak memiliki akses untuk menghapus materi ini.")
        return redirect(url_for('teacher.dashboard'))
    
    # Delete file if exists
    if material.get('file_path'):
        file_path = material['file_path']
        old_path = os.path.join('static/uploads', file_path)
        if os.path.exists(old_path):
            try:
                os.remove(old_path)
            except:
                pass
    
    MaterialModel.delete(material_id)
    flash("Materi berhasil dihapus.")
    return redirect(url_for('teacher.dashboard'))

# Quizzes
@teacher_bp.route('/quiz/create', methods=['GET', 'POST'])
@login_required
@teacher_required
@class_required
def create_quiz():
    class_id = session.get('selected_class_id')
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        # NEW: parse due_at and attempt_limit
        raw_due = request.form.get('due_at') or ''
        due_at = None
        if raw_due:
            try:
                # datetime-local => '%Y-%m-%dT%H:%M'
                due_at = datetime.strptime(raw_due, '%Y-%m-%dT%H:%M')
            except:
                flash("Format batas waktu tidak valid.")
                return render_template('teacher/create_quiz.html', edit=False, quiz=None)
        raw_limit = request.form.get('attempt_limit') or ''
        attempt_limit = None
        if raw_limit:
            try:
                attempt_limit = int(raw_limit)
                if attempt_limit <= 0:
                    flash("Batas percobaan harus lebih dari 0.")
                    return render_template('teacher/create_quiz.html', edit=False, quiz=None)
            except:
                flash("Batas percobaan harus berupa angka.")
                return render_template('teacher/create_quiz.html', edit=False, quiz=None)
        raw_duration = request.form.get('duration_minutes') or ''
        duration_minutes = None
        if raw_duration:
            try:
                duration_minutes = int(raw_duration)
                if duration_minutes <= 0:
                    flash("Durasi kuis harus lebih dari 0 menit.")
                    return render_template('teacher/create_quiz.html', edit=False, quiz=None)
            except:
                flash("Durasi kuis harus berupa angka (menit).")
                return render_template('teacher/create_quiz.html', edit=False, quiz=None)

        # NEW: parse num_options
        raw_num_options = request.form.get('num_options') or '5'
        num_options = 5
        try:
            num_options = int(raw_num_options)
            if num_options < 2 or num_options > 5:
                flash("Jumlah opsi jawaban harus antara 2-5.")
                return render_template('teacher/create_quiz.html', edit=False, quiz=None)
        except:
            flash("Jumlah opsi jawaban harus berupa angka.")
            return render_template('teacher/create_quiz.html', edit=False, quiz=None)

        if not title:
            flash("Judul kuis tidak boleh kosong.")
            return render_template('teacher/create_quiz.html', edit=False, quiz=None)
        
        try:
            quiz_id = QuizModel.create(title, class_id, session.get('user_id'), due_at, attempt_limit, duration_minutes, num_options)
            flash(f"Kuis '{title}' berhasil dibuat! Sekarang tambahkan pertanyaan.")
            return redirect(url_for('teacher.add_question', quiz_id=quiz_id))
        except Exception as e:
            flash(f"Gagal membuat kuis: {str(e)}")
    
    return render_template('teacher/create_quiz.html', edit=False, quiz=None)

@teacher_bp.route('/quiz/<int:quiz_id>/edit', methods=['GET', 'POST'])
@login_required
@teacher_required
def edit_quiz(quiz_id):
    from utils.database import get_db
    
    quiz = QuizModel.get_by_id(quiz_id)
    if not quiz:
        flash("Kuis tidak ditemukan.")
        return redirect(url_for('teacher.dashboard'))
    
    # Check if quiz belongs to teacher
    if quiz['created_by'] != session.get('user_id'):
        flash("Anda tidak memiliki akses untuk mengedit kuis ini.")
        return redirect(url_for('teacher.dashboard'))
    
    # Get question count
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT COUNT(*) as total FROM quiz_questions WHERE quiz_id=%s", (quiz_id,))
    question_count = cur.fetchone()['total']
    cur.close()
    quiz['total_questions'] = question_count
    
    # Load questions for listing on edit page
    questions = QuizQuestionModel.get_by_quiz(quiz_id)
    
    if request.method == 'POST':
        title = request.form['title'].strip()
        raw_due = request.form.get('due_at') or ''
        due_at = None
        if raw_due:
            try:
                due_at = datetime.strptime(raw_due, '%Y-%m-%dT%H:%M')
            except:
                flash("Format batas waktu tidak valid.")
                return render_template('teacher/edit_quiz.html', quiz=quiz, questions=questions)
        raw_limit = request.form.get('attempt_limit') or ''
        attempt_limit = None
        if raw_limit:
            try:
                attempt_limit = int(raw_limit)
                if attempt_limit <= 0:
                    flash("Batas percobaan harus lebih dari 0.")
                    return render_template('teacher/edit_quiz.html', quiz=quiz, questions=questions)
            except:
                flash("Batas percobaan harus berupa angka.")
                return render_template('teacher/edit_quiz.html', quiz=quiz, questions=questions)
        raw_duration = request.form.get('duration_minutes') or ''
        duration_minutes = None
        if raw_duration:
            try:
                duration_minutes = int(raw_duration)
                if duration_minutes <= 0:
                    flash("Durasi kuis harus lebih dari 0 menit.")
                    return render_template('teacher/edit_quiz.html', quiz=quiz, questions=questions)
            except:
                flash("Durasi kuis harus berupa angka (menit).")
                return render_template('teacher/edit_quiz.html', quiz=quiz, questions=questions)

        # NEW: parse num_options
        raw_num_options = request.form.get('num_options') or '5'
        num_options = 5
        try:
            num_options = int(raw_num_options)
            if num_options < 2 or num_options > 5:
                flash("Jumlah opsi jawaban harus antara 2-5.")
                return render_template('teacher/edit_quiz.html', quiz=quiz, questions=questions)
        except:
            flash("Jumlah opsi jawaban harus berupa angka.")
            return render_template('teacher/edit_quiz.html', quiz=quiz, questions=questions)

        if not title:
            flash("Judul kuis tidak boleh kosong.")
            return render_template('teacher/edit_quiz.html', quiz=quiz, questions=questions)

        QuizModel.update(quiz_id, title, due_at, attempt_limit, duration_minutes, num_options)
        flash("Kuis berhasil diperbarui.")
        return redirect(url_for('teacher.dashboard'))
    
    return render_template('teacher/edit_quiz.html', quiz=quiz, questions=questions)

@teacher_bp.route('/quiz/<int:quiz_id>/delete')
@login_required
@teacher_required
def delete_quiz(quiz_id):
    from utils.database import get_db
    
    quiz = QuizModel.get_by_id(quiz_id)
    if not quiz:
        flash("Kuis tidak ditemukan.")
        return redirect(url_for('teacher.dashboard'))
    
    # Check if quiz belongs to teacher
    if quiz['created_by'] != session.get('user_id'):
        flash("Anda tidak memiliki akses untuk menghapus kuis ini.")
        return redirect(url_for('teacher.dashboard'))
    
    db = get_db()
    cur = db.cursor()
    
    try:
        # Delete related data
        cur.execute("DELETE FROM quiz_answers WHERE quiz_id=%s", (quiz_id,))
        cur.execute("DELETE FROM quiz_scores WHERE quiz_id=%s", (quiz_id,))
        
        # Delete questions and their images
        cur.execute("SELECT id, image_path, audio_path, option_a_img, option_b_img, option_c_img, option_d_img, option_e_img FROM quiz_questions WHERE quiz_id=%s", (quiz_id,))
        questions = cur.fetchall()
        for q in questions:
            # q is a tuple; indexes: 0=id, 1=image_path, 2=audio_path, 3-7=option imgs
            paths = [q[1], q[2], q[3], q[4], q[5], q[6], q[7]]
            for pth in paths:
                if pth:
                    for old_file in [
                        os.path.join('static/uploads', pth),
                        os.path.join('static/uploads', pth.replace('uploads/', ''))
                    ]:
                        if os.path.exists(old_file):
                            try:
                                os.remove(old_file)
                                break
                            except:
                                pass
        
        cur.execute("DELETE FROM quiz_questions WHERE quiz_id=%s", (quiz_id,))
        cur.execute("DELETE FROM quizzes WHERE id=%s", (quiz_id,))
        
        db.commit()
        flash("Kuis berhasil dihapus.")
    except Exception as e:
        db.rollback()
        flash(f"Error menghapus kuis: {str(e)}")
    finally:
        cur.close()
    
    return redirect(url_for('teacher.dashboard'))

@teacher_bp.route('/quiz/<int:quiz_id>/add-question', methods=['GET', 'POST'])
@login_required
@teacher_required
def add_question(quiz_id):
    quiz = QuizModel.get_by_id(quiz_id)
    if not quiz:
        flash("Kuis tidak ditemukan.")
        return redirect(url_for('teacher.dashboard'))
    
    # Check if quiz belongs to teacher
    if quiz['created_by'] != session.get('user_id'):
        flash("Anda tidak memiliki akses untuk menambah pertanyaan pada kuis ini.")
        return redirect(url_for('teacher.dashboard'))
    
    questions = QuizQuestionModel.get_by_quiz(quiz_id)
    
    if request.method == 'POST':
        question_text = request.form.get('question', '').strip()
        a = request.form.get('a', '').strip()
        b = request.form.get('b', '').strip()
        c = request.form.get('c', '').strip()
        d = request.form.get('d', '').strip()
        e = request.form.get('e', '').strip()
        correct = request.form.get('correct', '').strip().lower()
        image_path = None
        audio_path = None
        # collect option image paths in a dict
        option_imgs = {'a': None, 'b': None, 'c': None, 'd': None, 'e': None}

        # Handle main question image (independent from audio)
        image_file = request.files.get('image')
        if image_file and image_file.filename:
            # Validate image file
            allowed_image_extensions = {'png', 'jpg', 'jpeg', 'gif'}
            image_ext = image_file.filename.rsplit('.', 1)[1].lower() if '.' in image_file.filename else ''
            
            if image_ext not in allowed_image_extensions:
                flash('Format gambar tidak diizinkan. Gunakan PNG, JPG, JPEG, atau GIF.')
                return render_template('teacher/add_question.html', quiz=quiz, questions=questions)
            
            try:
                # FIXED: Remove datetime from safe_name (save_uploaded_file handles this internally)
                image_path = save_uploaded_file(image_file, f"quiz_{quiz_id}")
            except Exception as e:
                flash(f'Gagal mengupload gambar: {str(e)}')
                return render_template('teacher/add_question.html', quiz=quiz, questions=questions)

        # Handle audio file (independent from image)
        audio_file = request.files.get('audio')
        if audio_file and audio_file.filename:
            # Validate audio file
            allowed_audio_extensions = {'mp3', 'wav', 'ogg', 'm4a'}
            audio_ext = audio_file.filename.rsplit('.', 1)[1].lower() if '.' in audio_file.filename else ''
            
            if audio_ext not in allowed_audio_extensions:
                flash('Format audio tidak diizinkan. Gunakan MP3, WAV, OGG, atau M4A.')
                return render_template('teacher/add_question.html', quiz=quiz, questions=questions)
            
            try:
                # FIXED: Remove datetime from safe_name (save_uploaded_file handles this internally)
                audio_path = save_uploaded_file(audio_file, f"quiz_{quiz_id}")
            except Exception as e:
                flash(f'Gagal mengupload audio: {str(e)}')
                return render_template('teacher/add_question.html', quiz=quiz, questions=questions)

        # Handle per-option images (A-E)
        allowed_image_extensions = {'png', 'jpg', 'jpeg', 'gif'}
        for key in ['a', 'b', 'c', 'd', 'e']:
            f = request.files.get(f"{key}_img")
            if f and f.filename:
                ext = f.filename.rsplit('.', 1)[1].lower() if '.' in f.filename else ''
                if ext not in allowed_image_extensions:
                    flash('Format gambar opsi tidak diizinkan. Gunakan PNG, JPG, JPEG, atau GIF.')
                    return render_template('teacher/add_question.html', quiz=quiz, questions=questions)
                try:
                    saved = save_uploaded_file(f, f"quiz_{quiz_id}")
                    option_imgs[key] = saved
                except Exception as e:
                    flash(f'Gagal mengupload gambar opsi: {str(e)}')
                    return render_template('teacher/add_question.html', quiz=quiz, questions=questions)

        try:
            QuizQuestionModel.create(
                quiz_id, question_text, a, b, c, d, e, correct, image_path,
                option_imgs['a'], option_imgs['b'], option_imgs['c'], option_imgs['d'], option_imgs['e'], audio_path
            )
            flash("Pertanyaan berhasil ditambahkan!")
            return redirect(url_for('teacher.add_question', quiz_id=quiz_id))
        except Exception as e:
            flash(f"Gagal menyimpan pertanyaan: {str(e)}")
            # Delete uploaded files if insert failed
            if image_path:
                try:
                    os.remove(os.path.join('static/uploads', image_path))
                except:
                    pass
            if audio_path:
                try:
                    os.remove(os.path.join('static/uploads', audio_path))
                except:
                    pass
    
    return render_template('teacher/add_question.html', quiz=quiz, questions=questions)

@teacher_bp.route('/quiz/<int:quiz_id>/question/<int:question_id>/edit', methods=['GET', 'POST'])
@login_required
@teacher_required
def edit_question(quiz_id, question_id):
    question = QuizQuestionModel.get_by_id(question_id)
    if not question:
        flash("Pertanyaan tidak ditemukan.")
        return redirect(url_for('teacher.add_question', quiz_id=quiz_id))
    
    if request.method == 'POST':
        question_text = request.form.get('question', '').strip()
        a = request.form.get('a', '').strip()
        b = request.form.get('b', '').strip()
        c = request.form.get('c', '').strip()
        d = request.form.get('d', '').strip()
        e = request.form.get('e', '').strip()
        correct = request.form.get('correct', '').strip().lower()
        image_path = question.get('image_path')
        audio_path = question.get('audio_path')
        # start with existing option images
        option_imgs = {
            'a': question.get('option_a_img'),
            'b': question.get('option_b_img'),
            'c': question.get('option_c_img'),
            'd': question.get('option_d_img'),
            'e': question.get('option_e_img'),
        }

        # Handle new main image (independent)
        image_file = request.files.get('image')
        if image_file and image_file.filename:
            # Validate image file
            allowed_image_extensions = {'png', 'jpg', 'jpeg', 'gif'}
            image_ext = image_file.filename.rsplit('.', 1)[1].lower() if '.' in image_file.filename else ''
            
            if image_ext not in allowed_image_extensions:
                flash('Format gambar tidak diizinkan. Gunakan PNG, JPG, JPEG, atau GIF.')
                return render_template('teacher/edit_question.html', question=question, quiz_id=quiz_id)
            
            # delete old main image if exists
            if image_path:
                old_paths = [
                    os.path.join('static/uploads', image_path),
                    os.path.join('static/uploads', image_path.replace('uploads/', ''))
                ]
                for old_file in old_paths:
                    if os.path.exists(old_file):
                        try:
                            os.remove(old_file)
                            break
                        except:
                            pass
            try:
                image_path = save_uploaded_file(image_file, f"quiz_{quiz_id}")
            except Exception as e:
                flash(f'Gagal mengupload gambar: {str(e)}')
                return render_template('teacher/edit_question.html', question=question, quiz_id=quiz_id)

        # Handle new audio file (independent)
        audio_file = request.files.get('audio')
        if audio_file and audio_file.filename:
            # Validate audio file
            allowed_audio_extensions = {'mp3', 'wav', 'ogg', 'm4a'}
            audio_ext = audio_file.filename.rsplit('.', 1)[1].lower() if '.' in audio_file.filename else ''
            
            if audio_ext not in allowed_audio_extensions:
                flash('Format audio tidak diizinkan. Gunakan MP3, WAV, OGG, atau M4A.')
                return render_template('teacher/edit_question.html', question=question, quiz_id=quiz_id)
            
            # delete old audio if exists
            if audio_path:
                old_paths = [
                    os.path.join('static/uploads', audio_path),
                    os.path.join('static/uploads', audio_path.replace('uploads/', ''))
                ]
                for old_file in old_paths:
                    if os.path.exists(old_file):
                        try:
                            os.remove(old_file)
                            break
                        except:
                            pass
            try:
                audio_path = save_uploaded_file(audio_file, f"quiz_{quiz_id}")
            except Exception as e:
                flash(f'Gagal mengupload audio: {str(e)}')
                return render_template('teacher/edit_question.html', question=question, quiz_id=quiz_id)

        # Handle per-option images replacement
        allowed_image_extensions = {'png', 'jpg', 'jpeg', 'gif'}
        for key in ['a', 'b', 'c', 'd', 'e']:
            f = request.files.get(f"{key}_img")
            if f and f.filename:
                ext = f.filename.rsplit('.', 1)[1].lower() if '.' in f.filename else ''
                if ext not in allowed_image_extensions:
                    flash('Format gambar opsi tidak diizinkan. Gunakan PNG, JPG, JPEG, atau GIF.')
                    return render_template('teacher/edit_question.html', question=question, quiz_id=quiz_id)
                # delete old option image
                old_path = option_imgs.get(key)
                if old_path:
                    for p in [os.path.join('static/uploads', old_path),
                              os.path.join('static/uploads', old_path.replace('uploads/', ''))]:
                        if os.path.exists(p):
                            try:
                                os.remove(p)
                                break
                            except:
                                pass
                try:
                    saved = save_uploaded_file(f, f"quiz_{quiz_id}")
                    option_imgs[key] = saved
                except Exception as e:
                    flash(f'Gagal mengupload gambar opsi: {str(e)}')
                    return render_template('teacher/edit_question.html', question=question, quiz_id=quiz_id)

        # Optional removal flags - handle image and audio separately
        if request.form.get('remove_image') == 'yes' and image_path:
            old_paths = [
                os.path.join('static/uploads', image_path),
                os.path.join('static/uploads', image_path.replace('uploads/', ''))
            ]
            for old_file in old_paths:
                if os.path.exists(old_file):
                    try:
                        os.remove(old_file)
                        break
                    except:
                        pass
            image_path = None
        
        # Optional removal flag for audio
        if request.form.get('remove_audio') == 'yes' and audio_path:
            old_paths = [
                os.path.join('static/uploads', audio_path),
                os.path.join('static/uploads', audio_path.replace('uploads/', ''))
            ]
            for old_file in old_paths:
                if os.path.exists(old_file):
                    try:
                        os.remove(old_file)
                        break
                    except:
                        pass
            audio_path = None
        
        # Optional removal for option images
        for key in ['a', 'b', 'c', 'd', 'e']:
            if request.form.get(f"remove_{key}_img") == 'yes' and option_imgs.get(key):
                old_path = option_imgs[key]
                for p in [os.path.join('static/uploads', old_path),
                          os.path.join('static/uploads', old_path.replace('uploads/', ''))]:
                    if os.path.exists(p):
                        try:
                            os.remove(p)
                            break
                        except:
                            pass
                option_imgs[key] = None

        try:
            QuizQuestionModel.update(
                question_id, question_text, a, b, c, d, e, correct, image_path,
                option_imgs['a'], option_imgs['b'], option_imgs['c'], option_imgs['d'], option_imgs['e'], audio_path
            )
            flash("Pertanyaan berhasil diperbarui!")
            return redirect(url_for('teacher.add_question', quiz_id=quiz_id))
        except Exception as e:
            flash(f"Gagal memperbarui pertanyaan: {str(e)}")
    
    return render_template('teacher/edit_question.html', question=question, quiz_id=quiz_id)

@teacher_bp.route('/quiz/<int:quiz_id>/question/<int:question_id>/delete')
@login_required
@teacher_required
def delete_question(quiz_id, question_id):
    question = QuizQuestionModel.get_by_id(question_id)
    if not question:
        flash("Pertanyaan tidak ditemukan.")
        return redirect(url_for('teacher.add_question', quiz_id=quiz_id))
    
    # Delete image if exists
    if question.get('image_path'):
        image_path = question['image_path']
        possible_paths = [
            os.path.join('static/uploads', image_path),
            os.path.join('static/uploads', image_path.replace('uploads/', ''))
        ]
        for path in possible_paths:
            if os.path.exists(path):
                try:
                    os.remove(path)
                    break
                except:
                    pass
    
    # Delete audio if exists
    if question.get('audio_path'):
        audio_path = question['audio_path']
        possible_paths = [
            os.path.join('static/uploads', audio_path),
            os.path.join('static/uploads', audio_path.replace('uploads/', ''))
        ]
        for path in possible_paths:
            if os.path.exists(path):
                try:
                    os.remove(path)
                    break
                except:
                    pass
    
    # Delete per-option images if exist
    for key in ['option_a_img', 'option_b_img', 'option_c_img', 'option_d_img', 'option_e_img']:
        img = question.get(key)
        if img:
            for path in [
                os.path.join('static/uploads', img),
                os.path.join('static/uploads', img.replace('uploads/', ''))
            ]:
                if os.path.exists(path):
                    try:
                        os.remove(path)
                        break
                    except:
                        pass
    
    # Delete from database
    from utils.database import get_db
    db = get_db()
    cur = db.cursor()
    
    try:
        # Delete student answers for this question
        cur.execute("DELETE FROM quiz_answers WHERE question_id=%s", (question_id,))
        # Delete the question
        cur.execute("DELETE FROM quiz_questions WHERE id=%s", (question_id,))
        db.commit()
        flash("Pertanyaan berhasil dihapus!")
    except Exception as e:
        db.rollback()
        flash(f"Gagal menghapus pertanyaan: {str(e)}")
    finally:
        cur.close()
    
    return redirect(url_for('teacher.add_question', quiz_id=quiz_id))

# Assignments
@teacher_bp.route('/assignment/create', methods=['GET', 'POST'])
@login_required
@teacher_required
@class_required
def create_assignment():
    class_id = session.get('selected_class_id')
    
    if request.method == 'POST':
        title = request.form['title'].strip()
        description = request.form['description']
        due_date = request.form.get('due_date') or None
        file_path = None
        
        # Handle file upload
        file = request.files.get('file')
        if file and file.filename:
            if not allowed_file(file.filename):
                flash('Format file tidak diizinkan.')
                return redirect(url_for('teacher.create_assignment'))
            
            try:
                safe_name = f"task_{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
                file_path = save_uploaded_file(file, "task")
            except Exception as e:
                flash(f'Gagal mengupload file: {str(e)}')
                return redirect(url_for('teacher.create_assignment'))
        
        AssignmentModel.create(title, description, class_id, session.get('user_id'), due_date, file_path)
        flash("Tugas berhasil dibuat.")
        return redirect(url_for('teacher.dashboard'))
    
    return render_template('teacher/create_assignment.html', edit=False, task=None)

@teacher_bp.route('/assignment/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
@teacher_required
def edit_assignment(task_id):
    task = AssignmentModel.get_by_id(task_id)
    if not task:
        flash("Tugas tidak ditemukan.")
        return redirect(url_for('teacher.dashboard'))
    
    # Check if task belongs to teacher
    if task['created_by'] != session.get('user_id'):
        flash("Anda tidak memiliki akses untuk mengedit tugas ini.")
        return redirect(url_for('teacher.dashboard'))
    
    if request.method == 'POST':
        title = request.form['title'].strip()
        description = request.form['description']
        due_date = request.form.get('due_date') or None
        file_path = task.get('file_path')
        
        # Handle file upload
        file = request.files.get('file')
        if file and file.filename:
            if not allowed_file(file.filename):
                flash('Format file tidak diizinkan.')
                return redirect(url_for('teacher.edit_assignment', task_id=task_id))
            
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
                safe_name = f"task_{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
                file_path = save_uploaded_file(file, "task")
            except Exception as e:
                flash(f'Gagal mengupload file: {str(e)}')
                return redirect(url_for('teacher.edit_assignment', task_id=task_id))
        
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
        
        AssignmentModel.update(task_id, title, description, due_date, file_path)
        flash("Tugas berhasil diperbarui.")
        return redirect(url_for('teacher.dashboard'))
    
    # FIX: provide 'now' so Jinja can compare due_date < now
    return render_template('teacher/create_assignment.html', edit=True, task=task, now=datetime.now())

@teacher_bp.route('/assignment/<int:task_id>/delete')
@login_required
@teacher_required
def delete_assignment(task_id):
    task = AssignmentModel.get_by_id(task_id)
    if not task:
        flash("Tugas tidak ditemukan.")
        return redirect(url_for('teacher.dashboard'))
    
    # Check if task belongs to teacher
    if task['created_by'] != session.get('user_id'):
        flash("Anda tidak memiliki akses untuk menghapus tugas ini.")
        return redirect(url_for('teacher.dashboard'))
    
    # Delete file if exists
    if task.get('file_path'):
        file_path = task['file_path']
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
    
    # Delete submissions and task
    from utils.database import get_db
    db = get_db()
    cur = db.cursor()
    
    try:
        # Delete submissions first
        cur.execute("DELETE FROM task_submissions WHERE task_id=%s", (task_id,))
        # Delete task
        cur.execute("DELETE FROM tasks WHERE id=%s", (task_id,))
        db.commit()
        flash("Tugas berhasil dihapus.")
    except Exception as e:
        db.rollback()
        flash(f"Error menghapus tugas: {str(e)}")
    finally:
        cur.close()
    
    return redirect(url_for('teacher.dashboard'))

@teacher_bp.route('/assignment/<int:task_id>/submissions')
@login_required
@teacher_required
def view_submissions(task_id):
    task = AssignmentModel.get_by_id(task_id)
    if not task:
        flash("Tugas tidak ditemukan.")
        return redirect(url_for('teacher.dashboard'))
    
    # Check if task belongs to teacher
    if task['created_by'] != session.get('user_id'):
        flash("Anda tidak memiliki akses untuk melihat submission tugas ini.")
        return redirect(url_for('teacher.dashboard'))
    
    submissions = AssignmentSubmissionModel.get_by_task(task_id)
    return render_template('teacher/view_submissions.html', task=task, submissions=submissions)

@teacher_bp.route('/submission/<int:submission_id>/grade', methods=['GET', 'POST'])
@login_required
@teacher_required
def grade_submission(submission_id):
    from utils.database import get_db
    
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("""
        SELECT ts.*, u.username, u.full_name, t.title as task_title, t.created_by
        FROM task_submissions ts
        JOIN users u ON ts.student_id = u.id
        JOIN tasks t ON ts.task_id = t.id
        WHERE ts.id = %s
    """, (submission_id,))
    submission = cur.fetchone()
    cur.close()
    
    if not submission:
        flash("Submission tidak ditemukan.")
        return redirect(url_for('teacher.dashboard'))
    
    # Check if task belongs to teacher
    if submission['created_by'] != session.get('user_id'):
        flash("Anda tidak memiliki akses untuk memberikan nilai pada submission ini.")
        return redirect(url_for('teacher.dashboard'))
    
    if request.method == 'POST':
        score = request.form.get('score', '').strip()
        feedback = request.form.get('feedback', '').strip()
        
        # Validate score
        try:
            score = float(score)
            if score < 0 or score > 100:
                flash("Nilai harus antara 0-100.")
                return redirect(url_for('teacher.grade_submission', submission_id=submission_id))
        except ValueError:
            flash("Nilai harus berupa angka.")
            return redirect(url_for('teacher.grade_submission', submission_id=submission_id))
        
        AssignmentSubmissionModel.update_grade(submission_id, score, feedback, session.get('user_id'))
        flash("Nilai berhasil diberikan.")
        return redirect(url_for('teacher.view_submissions', task_id=submission['task_id']))
    
    return render_template('teacher/grade_submission.html', submission=submission)

@teacher_bp.route('/students')
@login_required
@teacher_required
def list_students():
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("""
        SELECT u.id, u.username, u.full_name, u.avatar, u.bio,
               COUNT(DISTINCT e.class_id) as total_classes,
               COUNT(DISTINCT qs.id) as total_quiz_taken,
               COUNT(DISTINCT ts.id) as total_task_submitted
        FROM users u
        LEFT JOIN enrollments e ON u.id = e.user_id
        LEFT JOIN quiz_scores qs ON u.id = qs.student_id
        LEFT JOIN task_submissions ts ON u.id = ts.student_id
        WHERE u.role=%s
        GROUP BY u.id
        ORDER BY u.full_name, u.username
    """, ('student',))
    students = cur.fetchall()
    cur.close()

    # Render with dashboard-styled template
    from flask import render_template_string
    return render_template_string("""
    {% extends "navbar/base.html" %}
    {% block content %}
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');

        :root {
            --primary: #e11d48;
            --primary-dark: #b91c1c;
            --accent: #0ea5e9;
            --muted: #6b7280;
            --surface: #ffffff;
            --bg: #f8fafc;
            --shadow: 0 12px 28px rgba(15, 23, 42, 0.12);
            --border: #e5e7eb;
        }

        .students-page {
            font-family: 'Poppins', 'Segoe UI', sans-serif;
            color: #0f172a;
        }

        .page-hero {
            position: relative;
            overflow: hidden;
            background: radial-gradient(circle at 20% 20%, rgba(225, 29, 72, 0.14), transparent 35%),
                radial-gradient(circle at 85% 30%, rgba(14, 165, 233, 0.14), transparent 32%),
                linear-gradient(135deg, #fff7f8 0%, #f1f5f9 100%);
            border-radius: 18px;
            padding: 24px;
            margin-bottom: 26px;
            box-shadow: var(--shadow);
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 18px;
        }

        .page-hero::after {
            content: '';
            position: absolute;
            inset: 0;
            background: linear-gradient(135deg, rgba(225, 29, 72, 0.05), rgba(14, 165, 233, 0.04));
            pointer-events: none;
        }

        .hero-left, .hero-right {
            position: relative;
            z-index: 1;
        }

        .hero-left h1 {
            font-size: 30px;
            font-weight: 700;
            margin: 4px 0 8px 0;
        }

        .hero-left p {
            margin: 0;
            color: var(--muted);
            font-weight: 500;
        }

        .hero-icon {
            width: 72px;
            height: 72px;
            border-radius: 18px;
            background: linear-gradient(145deg, #0ea5e9, #0284c7);
            color: white;
            display: grid;
            place-items: center;
            font-size: 32px;
            box-shadow: 0 16px 35px rgba(14, 165, 233, 0.25);
        }

        .card {
            background: var(--surface);
            border-radius: 14px;
            box-shadow: var(--shadow);
            border: 1px solid var(--border);
        }

        .card-header {
            background: linear-gradient(135deg, #fff, #f8fafc);
            border-bottom: 1px solid var(--border);
            padding: 18px 20px;
        }

        .card-header h5 {
            margin: 0;
            color: #0f172a;
            font-weight: 700;
        }

        .card-header small {
            color: var(--muted);
        }

        .card-body {
            padding: 20px;
        }

        .students-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 20px;
        }

        .student-card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 14px;
            box-shadow: var(--shadow);
            padding: 20px;
            display: flex;
            flex-direction: column;
            transition: all 0.3s ease;
        }

        .student-card:hover {
            transform: translateY(-6px);
            box-shadow: 0 18px 40px rgba(15, 23, 42, 0.15);
            border-color: var(--accent);
        }

        .student-avatar {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: linear-gradient(145deg, #e11d48, #be123c);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 12px;
        }

        .student-name {
            font-size: 18px;
            font-weight: 700;
            color: #0f172a;
            margin: 0 0 4px 0;
        }

        .student-username {
            color: var(--muted);
            font-size: 13px;
            margin: 0 0 12px 0;
        }

        .student-stats {
            display: flex;
            flex-direction: column;
            gap: 8px;
            margin-bottom: 16px;
            padding-bottom: 12px;
            border-bottom: 1px solid var(--border);
        }

        .stat-row {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 13px;
            color: #0f172a;
        }

        .stat-row i {
            width: 20px;
            text-align: center;
            color: var(--accent);
        }

        .student-actions {
            display: flex;
            gap: 10px;
            margin-top: auto;
        }

        .btn-detail {
            flex: 1;
            padding: 10px 12px;
            font-size: 13px;
            border-radius: 8px;
            font-weight: 600;
            text-align: center;
            text-decoration: none;
            background-color: var(--primary);
            color: white;
            border: none;
            transition: all 0.2s ease;
        }

        .btn-detail:hover {
            background-color: var(--primary-dark);
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(225, 29, 72, 0.3);
        }

        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: var(--muted);
        }

        .empty-state i {
            font-size: 56px;
            margin-bottom: 16px;
            opacity: 0.3;
        }

        .empty-state p {
            font-size: 16px;
            margin: 0;
        }

        @media (max-width: 768px) {
            .page-hero {
                flex-direction: column;
                align-items: flex-start;
            }

            .students-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>

    <div class="students-page">
        <div class="page-hero">
            <div class="hero-left">
                <p><i class="fas fa-users me-1"></i>Manajemen Siswa</p>
                <h1>Daftar Siswa</h1>
            </div>
            <div class="hero-right">
                <div class="hero-icon"><i class="fas fa-users"></i></div>
            </div>
        </div>

        <div class="card">
            <div class="card-header">
                <h5><i class="fas fa-list me-2" style="color: var(--primary);"></i>Siswa Aktif</h5>
                <small>Lihat informasi dan riwayat aktivitas siswa</small>
            </div>
            <div class="card-body">
                {% if students %}
                <div class="students-grid">
                    {% for student in students %}
                    <div class="student-card">
                        <div class="student-avatar">{{ student.username[0]|upper }}</div>
                        <p class="student-name">{{ student.full_name or student.username }}</p>
                        <p class="student-username">@{{ student.username }}</p>
                        <div class="student-stats">
                            <div class="stat-row">
                                <i class="fas fa-book"></i>
                                {{ student.total_classes }} Kelas
                            </div>
                            <div class="stat-row">
                                <i class="fas fa-question-circle"></i>
                                {{ student.total_quiz_taken }} Kuis Dikerjakan
                            </div>
                            <div class="stat-row">
                                <i class="fas fa-tasks"></i>
                                {{ student.total_task_submitted }} Tugas Dikumpulkan
                            </div>
                        </div>
                        <div class="student-actions">
                            <a href="{{ url_for('teacher.view_student_detail', student_id=student.id) }}" class="btn-detail">
                                <i class="fas fa-eye me-1"></i>Lihat Detail
                            </a>
                        </div>
                    </div>
                    {% endfor %}
                </div>
                {% else %}
                <div class="empty-state">
                    <i class="fas fa-users"></i>
                    <p>Tidak ada siswa</p>
                </div>
                {% endif %}
            </div>
        </div>
    </div>
    {% endblock %}
    """, students=students)

@teacher_bp.route('/students/<int:student_id>')
@login_required
@teacher_required
def view_student_detail(student_id):
    # Basic student info
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT id, username, full_name, bio, avatar FROM users WHERE id=%s AND role=%s", (student_id, 'student'))
    student = cur.fetchone()
    if not student:
        cur.close()
        flash("Siswa tidak ditemukan.")
        return redirect(url_for('teacher.list_students'))

    # Quiz scores for the student
    cur.execute("""
        SELECT 
            qs.id as score_id,
            qs.score,
            qs.graded_at,
            q.id as quiz_id,
            q.title as quiz_title,
            c.name as class_name,
            (SELECT COUNT(*) FROM quiz_questions WHERE quiz_id = q.id) as total_questions
        FROM quiz_scores qs
        JOIN quizzes q ON qs.quiz_id = q.id
        LEFT JOIN classes c ON q.class_id = c.id
        WHERE qs.student_id = %s
        ORDER BY qs.graded_at DESC
    """, (student_id,))
    quiz_history = cur.fetchall()

    # Task submissions for the student
    cur.execute("""
        SELECT 
            ts.id as submission_id,
            ts.score,
            ts.submitted_at,
            ts.graded_at,
            ts.feedback,
            t.id as task_id,
            t.title as task_title,
            c.name as class_name
        FROM task_submissions ts
        JOIN tasks t ON ts.task_id = t.id
        LEFT JOIN classes c ON t.class_id = c.id
        WHERE ts.student_id = %s
        ORDER BY ts.submitted_at DESC
    """, (student_id,))
    task_submissions = cur.fetchall()
    cur.close()

    # Minimal HTML without new template file
    from flask import render_template_string
    return render_template_string("""
    {% extends "navbar/base.html" %}
    {% block content %}
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');

    :root {
        --primary: #e11d48;
        --primary-dark: #b91c1c;
        --accent: #0ea5e9;
        --warning: #f59e0b;
        --success: #10b981;
        --muted: #6b7280;
        --surface: #ffffff;
        --bg: #f8fafc;
        --shadow: 0 12px 28px rgba(15, 23, 42, 0.12);
        --border: #e5e7eb;
    }

    .student-detail-page {
        font-family: 'Poppins', 'Segoe UI', sans-serif;
        color: #0f172a;
        background: var(--bg);
    }

    .page-hero {
        position: relative;
        overflow: hidden;
        background: radial-gradient(circle at 20% 20%, rgba(225, 29, 72, 0.14), transparent 35%),
            radial-gradient(circle at 85% 30%, rgba(14, 165, 233, 0.14), transparent 32%),
            linear-gradient(135deg, #fff7f8 0%, #f1f5f9 100%);
        border-radius: 18px;
        padding: 24px;
        margin-bottom: 26px;
        box-shadow: var(--shadow);
    }

    .page-hero h1 {
        font-size: 30px;
        font-weight: 700;
        margin: 4px 0 8px 0;
        color: #0f172a;
    }

    .page-hero p {
        margin: 0;
        color: var(--muted);
        font-weight: 500;
    }

    .card {
        background: var(--surface);
        border-radius: 14px;
        box-shadow: var(--shadow);
        border: 1px solid var(--border);
        margin-bottom: 22px;
    }

    .card-header {
        background: linear-gradient(135deg, #fff, #f8fafc);
        border-bottom: 1px solid var(--border);
        padding: 18px 20px;
        border-radius: 14px 14px 0 0;
    }

    .card-header h5 {
        margin: 0;
        color: #0f172a;
        font-weight: 700;
        font-size: 18px;
    }

    .card-body {
        padding: 24px;
    }

    .student-info-card {
        background: linear-gradient(135deg, #fff1f2 0%, #ffe4e6 100%);
        border: 1px solid #fecdd3;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 24px;
    }

    .student-info-card h5 {
        color: var(--primary-dark);
        font-weight: 700;
        margin-bottom: 8px;
        font-size: 20px;
    }

    .student-info-card p {
        color: var(--muted);
        margin: 0;
        font-size: 14px;
    }

    .section-title {
        font-size: 20px;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .section-title i {
        color: var(--primary);
    }

    .table {
        margin-bottom: 0;
    }

    .table thead th {
        background: #f8fafc;
        color: #0f172a;
        font-weight: 700;
        border-bottom: 1px solid var(--border);
        padding: 14px;
        font-size: 13px;
    }

    .table tbody td {
        padding: 14px;
        border-bottom: 1px solid #eef2f7;
        color: #0f172a;
        vertical-align: middle;
        font-size: 14px;
    }

    .table tbody tr:hover {
        background: #f8fafc;
    }

    .btn-outline-secondary {
        border-color: #64748b;
        color: #64748b;
        border-width: 1.5px;
        font-weight: 600;
        border-radius: 8px;
        padding: 6px 12px;
        font-size: 13px;
    }

    .btn-outline-secondary:hover {
        background: #64748b;
        color: white;
    }

    .empty-state {
        text-align: center;
        padding: 40px 20px;
        color: var(--muted);
        font-size: 14px;
    }

    .empty-state i {
        font-size: 42px;
        margin-bottom: 12px;
        opacity: 0.5;
        color: var(--primary);
    }

    .badge {
        padding: 6px 12px;
        border-radius: 999px;
        font-weight: 600;
        font-size: 12px;
    }
    </style>

    <div class="student-detail-page">
      <div class="page-hero">
        <p><i class="fas fa-user-graduate me-1"></i>Profil Siswa</p>
        <h1>Detail Siswa</h1>
      </div>

      <div class="student-info-card">
        <h5><i class="fas fa-user-circle me-2"></i>{{ student.full_name or student.username }}</h5>
        <p>{{ student.bio or 'Tidak ada bio.' }}</p>
      </div>

      <div class="card">
        <div class="card-header">
          <h5><i class="fas fa-question-circle me-2" style="color: #0ea5e9;"></i>Riwayat Kuis</h5>
        </div>
        <div class="card-body">
          {% if quiz_history %}
          <div class="table-responsive">
            <table class="table">
              <thead>
                <tr>
                  <th>Judul Kuis</th>
                  <th>Kelas</th>
                  <th>Pertanyaan</th>
                  <th>Nilai</th>
                  <th>Dinilai</th>
                  <th>Aksi</th>
                </tr>
              </thead>
              <tbody>
                {% for h in quiz_history %}
                <tr>
                  <td><strong>{{ h.quiz_title }}</strong></td>
                  <td>{{ h.class_name or '-' }}</td>
                  <td><span class="badge" style="background: #e0f2fe; color: #0c4a6e;">{{ h.total_questions }} soal</span></td>
                  <td><strong style="color: #10b981;">{{ h.score }}%</strong></td>
                  <td>{{ h.graded_at.strftime('%d %b %Y %H:%M') if h.graded_at else '-' }}</td>
                  <td>
                    <a class="btn btn-sm btn-outline-secondary" href="{{ url_for('teacher.view_student_quiz_detail', student_id=student.id, quiz_id=h.quiz_id, score_id=h.score_id) }}">
                      <i class="fas fa-eye me-1"></i>Detail
                    </a>
                  </td>
                </tr>
                {% endfor %}
              </tbody>
            </table>
          </div>
          {% else %}
            <div class="empty-state">
              <i class="fas fa-question-circle"></i>
              <p>Belum ada riwayat kuis.</p>
            </div>
          {% endif %}
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h5><i class="fas fa-tasks me-2" style="color: #f59e0b;"></i>Submission Tugas</h5>
        </div>
        <div class="card-body">
          {% if task_submissions %}
          <div class="table-responsive">
            <table class="table">
              <thead>
                <tr>
                  <th>Tugas</th>
                  <th>Kelas</th>
                  <th>Diunggah</th>
                  <th>Nilai</th>
                  <th>Dinilai</th>
                  <th>Feedback</th>
                </tr>
              </thead>
              <tbody>
                {% for s in task_submissions %}
                <tr>
                  <td><strong>{{ s.task_title }}</strong></td>
                  <td>{{ s.class_name or '-' }}</td>
                  <td>{{ s.submitted_at.strftime('%d %b %Y %H:%M') if s.submitted_at else '-' }}</td>
                  <td>
                    {% if s.score is not none %}
                    <strong style="color: #10b981;">{{ s.score }}</strong>
                    {% else %}
                    <span class="text-muted">-</span>
                    {% endif %}
                  </td>
                  <td>{{ s.graded_at.strftime('%d %b %Y %H:%M') if s.graded_at else '-' }}</td>
                  <td style="max-width:380px;">{{ s.feedback or '-' }}</td>
                </tr>
                {% endfor %}
              </tbody>
            </table>
          </div>
          {% else %}
            <div class="empty-state">
              <i class="fas fa-tasks"></i>
              <p>Belum ada submission tugas.</p>
            </div>
          {% endif %}
        </div>
      </div>
    </div>
    {% endblock %}
    """, student=student, quiz_history=quiz_history, task_submissions=task_submissions)

@teacher_bp.route('/students/<int:student_id>/quiz/<int:quiz_id>/history/<int:score_id>')
@login_required
@teacher_required
def view_student_quiz_detail(student_id, quiz_id, score_id):
    # Verify target student exists
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT id, username, full_name FROM users WHERE id=%s AND role=%s", (student_id, 'student'))
    student = cur.fetchone()
    if not student:
        cur.close()
        flash("Siswa tidak ditemukan.")
        return redirect(url_for('teacher.list_students'))

    # Load the score record
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
        WHERE qs.id = %s AND qs.student_id = %s AND qs.quiz_id = %s
    """, (score_id, student_id, quiz_id))
    score = cur.fetchone()
    if not score:
        cur.close()
        flash("Data kuis tidak ditemukan.")
        return redirect(url_for('teacher.view_student_detail', student_id=student_id))

    # Detailed answers
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
    """, (student_id, quiz_id, quiz_id))
    answers = cur.fetchall()
    cur.close()

    total_questions = len(answers)
    correct_answers = sum(1 for a in answers if a.get('is_correct'))
    wrong_answers = total_questions - correct_answers
    answer_stats = {'total': total_questions, 'correct': correct_answers, 'wrong': wrong_answers}

    # Minimal HTML without new template file
    from flask import render_template_string
    return render_template_string("""
    {% extends "navbar/base.html" %}
    {% block content %}
    <div class="container">
      <h2>Detail Kuis Siswa</h2>
      <div class="mb-2">
        <strong>{{ student.full_name or student.username }}</strong>
      </div>

      <div style="border:1px solid #ddd; border-radius:8px; padding:12px; margin-bottom:12px;">
        <div><strong>{{ score.quiz_title }}</strong></div>
        <div style="font-size:13px; color:#666;">
          Kelas: {{ score.class_name or '-' }} •
          Dinilai: {{ score.graded_at.strftime('%d %b %Y %H:%M') if score.graded_at else '-' }}
        </div>
        <div style="margin-top:8px; font-weight:bold;">Nilai: {{ score.score }}%</div>
      </div>

      <div style="border:1px solid #eee; border-radius:8px; padding:10px; margin-bottom:12px;">
        <strong>Ringkasan Jawaban</strong>
        <div style="font-size:13px; color:#444; margin-top:6px;">
          Total: {{ answer_stats.total }} • Benar: {{ answer_stats.correct }} • Salah: {{ answer_stats.wrong }}
        </div>
      </div>

      {% if answers %}
        <div>
          {% for a in answers %}
            <div style="border:1px solid #f0f0f0; border-radius:8px; padding:10px; margin-bottom:8px;">
              <div style="margin-bottom:6px;"><strong>Soal {{ loop.index }}:</strong> {{ a.question }}</div>
              <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap:6px; font-size:13px;">
                <div>A. {{ a.option_a or '-' }}</div>
                <div>B. {{ a.option_b or '-' }}</div>
                <div>C. {{ a.option_c or '-' }}</div>
                <div>D. {{ a.option_d or '-' }}</div>
                {% if a.option_e %}<div>E. {{ a.option_e }}</div>{% endif %}
              </div>
              <div style="margin-top:8px; font-size:13px;">
                Jawaban siswa: <strong>{{ a.selected_option|upper if a.selected_option else '-' }}</strong> •
                Kunci: <strong>{{ a.correct_option|upper if a.correct_option else '-' }}</strong> •
                Status:
                {% if a.is_correct %}
                  <span style="color:green; font-weight:bold;">Benar</span>
                {% else %}
                  <span style="color:#d00; font-weight:bold;">Salah</span>
                {% endif %}
              </div>
            </div>
          {% endfor %}
        </div>
      {% else %}
        <p>Detail jawaban tidak tersedia.</p>
      {% endif %}

      <div style="margin-top:12px;">
        <a href="{{ url_for('teacher.view_student_detail', student_id=student.id) }}">Kembali ke detail siswa</a>
      </div>
    </div>
    {% endblock %}
    """, student=student, score=score, answers=answers, answer_stats=answer_stats)

@teacher_bp.route('/quiz/<int:quiz_id>/submissions')
@login_required
@teacher_required
def view_quiz_submissions(quiz_id):
    from utils.database import get_db
    db = get_db()
    cur = db.cursor(dictionary=True)

    # Verify quiz exists and belongs to selected class (optional)
    quiz = QuizModel.get_by_id(quiz_id)
    if not quiz:
        flash("Kuis tidak ditemukan.")
        return redirect(url_for('teacher.dashboard'))

    # Optional: restrict by teacher ownership
    if quiz.get('created_by') != session.get('user_id'):
        flash("Anda tidak memiliki akses untuk melihat submission kuis ini.")
        return redirect(url_for('teacher.dashboard'))

    # Load submissions (scores)
    cur.execute("""
        SELECT 
            qs.id as score_id,
            qs.student_id,
            qs.score,
            qs.graded_at,
            u.username,
            u.full_name,
            c.name as class_name,
            (SELECT COUNT(*) FROM quiz_questions WHERE quiz_id=%s) as total_questions
        FROM quiz_scores qs
        JOIN users u ON qs.student_id = u.id
        LEFT JOIN classes c ON %s = c.id
        WHERE qs.quiz_id = %s
        ORDER BY qs.graded_at DESC
    """, (quiz_id, quiz.get('class_id'), quiz_id))
    submissions = cur.fetchall()
    cur.close()

    # Minimal HTML using render_template_string (no new template file)
    from flask import render_template_string
    return render_template_string("""
    {% extends "navbar/base.html" %}
    {% block title %}Submission Kuis - {{ quiz.title }}{% endblock %}
    {% block content %}
    <div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
        <h1 class="h2">Submission Kuis</h1>
        <div>
            <a href="{{ url_for('teacher.edit_quiz', quiz_id=quiz.id) }}" class="btn btn-outline-primary me-2">Kembali ke Edit Kuis</a>
            <a href="{{ url_for('teacher.dashboard') }}" class="btn btn-secondary">Dashboard</a>
        </div>
    </div>

    <div class="card">
      <div class="card-header d-flex justify-content-between align-items-center">
        <h5 class="card-title mb-0">Kuis: {{ quiz.title }}</h5>
        <span class="badge bg-primary">{{ submissions|length }} submission</span>
      </div>
      <div class="card-body">
        {% if submissions %}
        <div class="table-responsive">
          <table class="table table-striped">
            <thead>
              <tr>
                <th>Nama</th>
                <th>Username</th>
                <th>Nilai</th>
                <th>Pertanyaan</th>
                <th>Dinilai</th>
                <th>Aksi</th>
              </tr>
            </thead>
            <tbody>
              {% for s in submissions %}
              <tr>
                <td>{{ s.full_name or '-' }}</td>
                <td>{{ s.username }}</td>
                <td><strong>{{ s.score }}%</strong></td>
                <td>{{ s.total_questions }}</td>
                <td>{{ s.graded_at.strftime('%d %b %Y %H:%M') if s.graded_at else '-' }}</td>
                <td>
                  <a class="btn btn-sm btn-outline-secondary" href="{{ url_for('teacher.view_student_quiz_detail', student_id=s.student_id, quiz_id=quiz.id, score_id=s.score_id) }}">Detail</a>
                </td>
              </tr>
              {% endfor %}
            </tbody>
          </table>
        </div>
        {% else %}
          <p class="text-muted">Belum ada siswa yang mengerjakan kuis ini.</p>
        {% endif %}
      </div>
    </div>
    {% endblock %}
    """, quiz=quiz, submissions=submissions)