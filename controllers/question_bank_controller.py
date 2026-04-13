from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils.authentication import login_required, teacher_required
from models.question_bank_model import (
    QuestionBankModel, BankQuestionModel, 
    AssignmentBankModel, MaterialBankModel
)
from models.quiz_model import QuizModel, QuizQuestionModel
from models.assignment_model import AssignmentModel
from utils.file_handler import allowed_file, save_uploaded_file
from utils.database import get_db
import os
from datetime import datetime

question_bank_bp = Blueprint('question_bank', __name__, url_prefix='/bank')

# ============== QUESTION BANK MANAGEMENT ==============

@question_bank_bp.route('/')
@login_required
@teacher_required
def index():
    """Tampilkan daftar semua bank soal guru"""
    teacher_id = session.get('user_id')
    banks = QuestionBankModel.get_by_teacher(teacher_id)
    
    assignment_banks = AssignmentBankModel.get_by_teacher(teacher_id)
    material_banks = MaterialBankModel.get_by_teacher(teacher_id)
    
    return render_template('teacher/question_bank/index.html', 
                         banks=banks,
                         assignment_banks=assignment_banks,
                         material_banks=material_banks)

@question_bank_bp.route('/create', methods=['GET', 'POST'])
@login_required
@teacher_required
def create_bank():
    """Buat bank soal baru"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        
        if not name:
            flash("Nama bank soal tidak boleh kosong.")
            return render_template('teacher/question_bank/create_bank.html')
        
        try:
            bank_id = QuestionBankModel.create(name, session.get('user_id'), description)
            flash(f"Bank soal '{name}' berhasil dibuat.")
            return redirect(url_for('question_bank.view_bank', bank_id=bank_id))
        except Exception as e:
            flash(f"Gagal membuat bank soal: {str(e)}")
    
    return render_template('teacher/question_bank/create_bank.html')

@question_bank_bp.route('/<int:bank_id>')
@login_required
@teacher_required
def view_bank(bank_id):
    """Lihat detail bank soal dan daftar pertanyaannya"""
    bank = QuestionBankModel.get_by_id(bank_id)
    if not bank:
        flash("Bank soal tidak ditemukan.")
        return redirect(url_for('question_bank.index'))
    
    # Check access
    if bank['created_by'] != session.get('user_id'):
        flash("Anda tidak memiliki akses ke bank soal ini.")
        return redirect(url_for('question_bank.index'))
    
    questions = BankQuestionModel.get_by_bank(bank_id)
    
    return render_template('teacher/question_bank/view_bank.html', 
                         bank=bank, 
                         questions=questions)

@question_bank_bp.route('/<int:bank_id>/edit', methods=['GET', 'POST'])
@login_required
@teacher_required
def edit_bank(bank_id):
    """Edit informasi bank soal"""
    bank = QuestionBankModel.get_by_id(bank_id)
    if not bank:
        flash("Bank soal tidak ditemukan.")
        return redirect(url_for('question_bank.index'))
    
    # Check access
    if bank['created_by'] != session.get('user_id'):
        flash("Anda tidak memiliki akses ke bank soal ini.")
        return redirect(url_for('question_bank.index'))
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        
        if not name:
            flash("Nama bank soal tidak boleh kosong.")
            return render_template('teacher/question_bank/edit_bank.html', bank=bank)
        
        try:
            QuestionBankModel.update(bank_id, name, description)
            flash("Bank soal berhasil diperbarui.")
            return redirect(url_for('question_bank.view_bank', bank_id=bank_id))
        except Exception as e:
            flash(f"Gagal memperbarui bank soal: {str(e)}")
    
    return render_template('teacher/question_bank/edit_bank.html', bank=bank)

@question_bank_bp.route('/<int:bank_id>/delete')
@login_required
@teacher_required
def delete_bank(bank_id):
    """Hapus bank soal"""
    bank = QuestionBankModel.get_by_id(bank_id)
    if not bank:
        flash("Bank soal tidak ditemukan.")
        return redirect(url_for('question_bank.index'))
    
    # Check access
    if bank['created_by'] != session.get('user_id'):
        flash("Anda tidak memiliki akses ke bank soal ini.")
        return redirect(url_for('question_bank.index'))
    
    try:
        QuestionBankModel.delete(bank_id)
        flash("Bank soal berhasil dihapus.")
    except Exception as e:
        flash(f"Gagal menghapus bank soal: {str(e)}")
    
    return redirect(url_for('question_bank.index'))


# ============== QUESTION IN BANK MANAGEMENT ==============

@question_bank_bp.route('/<int:bank_id>/question/add', methods=['GET', 'POST'])
@login_required
@teacher_required
def add_question(bank_id):
    """Tambah pertanyaan ke bank soal"""
    bank = QuestionBankModel.get_by_id(bank_id)
    if not bank:
        flash("Bank soal tidak ditemukan.")
        return redirect(url_for('question_bank.index'))
    
    # Check access
    if bank['created_by'] != session.get('user_id'):
        flash("Anda tidak memiliki akses ke bank soal ini.")
        return redirect(url_for('question_bank.index'))
    
    # Get existing questions untuk ditampilkan di sidebar
    questions = BankQuestionModel.get_by_bank(bank_id)
    
    if request.method == 'POST':
        # Ambil data dari form dengan nama field yang sesuai dengan HTML
        question_text = request.form.get('question', '').strip()
        option_a = request.form.get('a', '').strip()
        option_b = request.form.get('b', '').strip()
        option_c = request.form.get('c', '').strip()
        option_d = request.form.get('d', '').strip()
        option_e = request.form.get('e', '').strip()
        correct_option = request.form.get('correct', '').strip().upper()
        num_options = request.form.get('num_options', '5')
        
        # Convert num_options to integer
        try:
            num_options_int = int(num_options)
        except:
            num_options_int = 5
        
        # Validasi berdasarkan jumlah opsi yang dipilih
        required_options = [question_text, option_a, option_b]
        
        if num_options_int >= 3:
            required_options.append(option_c)
        if num_options_int >= 4:
            required_options.append(option_d)
        if num_options_int >= 5:
            required_options.append(option_e)
        
        required_options.append(correct_option)
        
        if not all(required_options):
            flash("Semua field wajib diisi sesuai jumlah opsi yang dipilih.")
            return render_template('teacher/question_bank/add_question.html', 
                                 bank=bank, questions=questions)
        
        # Validasi correct_option
        valid_options = ['A', 'B', 'C', 'D', 'E'][:num_options_int]
        if correct_option not in valid_options:
            flash(f"Pilihan jawaban benar harus salah satu dari: {', '.join(valid_options)}")
            return render_template('teacher/question_bank/add_question.html', 
                                 bank=bank, questions=questions)
        
        image_path = None
        audio_path = None
        option_a_img = None
        option_b_img = None
        option_c_img = None
        option_d_img = None
        option_e_img = None
        
        # Handle file uploads dengan nama field yang sesuai
        try:
            # Upload gambar pertanyaan (nama field: 'image')
            if 'image' in request.files and request.files['image'].filename:
                image_path = save_uploaded_file(request.files['image'], 'question')
            
            # Upload audio
            if 'audio' in request.files and request.files['audio'].filename:
                audio_path = save_uploaded_file(request.files['audio'], 'audio')
            
            # Upload gambar opsi (nama field: 'a_img', 'b_img', dll)
            if 'a_img' in request.files and request.files['a_img'].filename:
                option_a_img = save_uploaded_file(request.files['a_img'], 'question')
            
            if 'b_img' in request.files and request.files['b_img'].filename:
                option_b_img = save_uploaded_file(request.files['b_img'], 'question')
            
            if 'c_img' in request.files and request.files['c_img'].filename:
                option_c_img = save_uploaded_file(request.files['c_img'], 'question')
            
            if 'd_img' in request.files and request.files['d_img'].filename:
                option_d_img = save_uploaded_file(request.files['d_img'], 'question')
            
            if 'e_img' in request.files and request.files['e_img'].filename:
                option_e_img = save_uploaded_file(request.files['e_img'], 'question')
        except Exception as e:
            flash(f"Gagal upload file: {str(e)}")
            return render_template('teacher/question_bank/add_question.html', 
                                 bank=bank, questions=questions)
        
        try:
            BankQuestionModel.create(
                bank_id, question_text, option_a, option_b, option_c, option_d, option_e,
                correct_option, image_path, option_a_img, option_b_img, option_c_img,
                option_d_img, option_e_img, audio_path
            )
            flash("Pertanyaan berhasil ditambahkan ke bank soal.")
            
            # Redirect kembali ke halaman add question untuk menambah lagi
            return redirect(url_for('question_bank.add_question', bank_id=bank_id))
        except Exception as e:
            flash(f"Gagal menambah pertanyaan: {str(e)}")
    
    return render_template('teacher/question_bank/add_question.html', 
                         bank=bank, questions=questions)

@question_bank_bp.route('/<int:bank_id>/question/<int:question_id>/edit', methods=['GET', 'POST'])
@login_required
@teacher_required
def edit_question(bank_id, question_id):
    """Edit pertanyaan di bank soal"""
    question = BankQuestionModel.get_by_id(question_id)
    if not question:
        flash("Pertanyaan tidak ditemukan.")
        return redirect(url_for('question_bank.index'))
    
    bank = QuestionBankModel.get_by_id(question['bank_id'])
    if bank['created_by'] != session.get('user_id'):
        flash("Anda tidak memiliki akses ke pertanyaan ini.")
        return redirect(url_for('question_bank.index'))
    
    # Get existing questions untuk ditampilkan di sidebar
    questions = BankQuestionModel.get_by_bank(bank_id)
    
    if request.method == 'POST':
        # Ambil data dari form
        question_text = request.form.get('question', '').strip()
        option_a = request.form.get('a', '').strip()
        option_b = request.form.get('b', '').strip()
        option_c = request.form.get('c', '').strip()
        option_d = request.form.get('d', '').strip()
        option_e = request.form.get('e', '').strip()
        correct_option = request.form.get('correct', '').strip().upper()
        num_options = request.form.get('num_options', '5')
        
        # Convert num_options to integer
        try:
            num_options_int = int(num_options)
        except:
            num_options_int = 5
        
        # Validasi berdasarkan jumlah opsi yang dipilih
        required_options = [question_text, option_a, option_b]
        
        if num_options_int >= 3:
            required_options.append(option_c)
        if num_options_int >= 4:
            required_options.append(option_d)
        if num_options_int >= 5:
            required_options.append(option_e)
        
        required_options.append(correct_option)
        
        if not all(required_options):
            flash("Semua field wajib diisi sesuai jumlah opsi yang dipilih.")
            return render_template('teacher/question_bank/edit_question.html', 
                                 question=question, bank=bank, questions=questions)
        
        # Validasi correct_option
        valid_options = ['A', 'B', 'C', 'D', 'E'][:num_options_int]
        if correct_option not in valid_options:
            flash(f"Pilihan jawaban benar harus salah satu dari: {', '.join(valid_options)}")
            return render_template('teacher/question_bank/edit_question.html', 
                                 question=question, bank=bank, questions=questions)
        
        # Gunakan path file yang sudah ada
        image_path = question.get('image_path')
        audio_path = question.get('audio_path')
        option_a_img = question.get('option_a_img')
        option_b_img = question.get('option_b_img')
        option_c_img = question.get('option_c_img')
        option_d_img = question.get('option_d_img')
        option_e_img = question.get('option_e_img')
        
        # Handle file uploads
        try:
            # Upload gambar pertanyaan
            if 'image' in request.files and request.files['image'].filename:
                if image_path:
                    old_path = os.path.join('static/uploads', image_path)
                    if os.path.exists(old_path):
                        try:
                            os.remove(old_path)
                        except:
                            pass
                image_path = save_uploaded_file(request.files['image'], 'question')
            
            # Upload audio
            if 'audio' in request.files and request.files['audio'].filename:
                if audio_path:
                    old_path = os.path.join('static/uploads', audio_path)
                    if os.path.exists(old_path):
                        try:
                            os.remove(old_path)
                        except:
                            pass
                audio_path = save_uploaded_file(request.files['audio'], 'audio')
            
            # Handle option images
            if 'a_img' in request.files and request.files['a_img'].filename:
                if option_a_img:
                    try:
                        os.remove(os.path.join('static/uploads', option_a_img))
                    except:
                        pass
                option_a_img = save_uploaded_file(request.files['a_img'], 'question')
            
            if 'b_img' in request.files and request.files['b_img'].filename:
                if option_b_img:
                    try:
                        os.remove(os.path.join('static/uploads', option_b_img))
                    except:
                        pass
                option_b_img = save_uploaded_file(request.files['b_img'], 'question')
            
            if 'c_img' in request.files and request.files['c_img'].filename:
                if option_c_img:
                    try:
                        os.remove(os.path.join('static/uploads', option_c_img))
                    except:
                        pass
                option_c_img = save_uploaded_file(request.files['c_img'], 'question')
            
            if 'd_img' in request.files and request.files['d_img'].filename:
                if option_d_img:
                    try:
                        os.remove(os.path.join('static/uploads', option_d_img))
                    except:
                        pass
                option_d_img = save_uploaded_file(request.files['d_img'], 'question')
            
            if 'e_img' in request.files and request.files['e_img'].filename:
                if option_e_img:
                    try:
                        os.remove(os.path.join('static/uploads', option_e_img))
                    except:
                        pass
                option_e_img = save_uploaded_file(request.files['e_img'], 'question')
        except Exception as e:
            flash(f"Gagal upload file: {str(e)}")
            return render_template('teacher/question_bank/edit_question.html', 
                                 question=question, bank=bank, questions=questions)
        
        try:
            BankQuestionModel.update(
                question_id, question_text, option_a, option_b, option_c, option_d, option_e,
                correct_option, image_path, option_a_img, option_b_img, option_c_img,
                option_d_img, option_e_img, audio_path
            )
            flash("Pertanyaan berhasil diperbarui.")
            return redirect(url_for('question_bank.view_bank', bank_id=question['bank_id']))
        except Exception as e:
            flash(f"Gagal memperbarui pertanyaan: {str(e)}")
    
    return render_template('teacher/question_bank/edit_question.html', 
                         question=question, bank=bank, questions=questions)

@question_bank_bp.route('/<int:bank_id>/question/<int:question_id>/delete')
@login_required
@teacher_required
def delete_question(bank_id, question_id):
    """Hapus pertanyaan dari bank soal"""
    question = BankQuestionModel.get_by_id(question_id)
    if not question:
        flash("Pertanyaan tidak ditemukan.")
        return redirect(url_for('question_bank.index'))
    
    bank = QuestionBankModel.get_by_id(question['bank_id'])
    if bank['created_by'] != session.get('user_id'):
        flash("Anda tidak memiliki akses ke pertanyaan ini.")
        return redirect(url_for('question_bank.index'))
    
    try:
        # Delete files if exist
        for file_field in ['image_path', 'audio_path', 'option_a_img', 'option_b_img', 
                          'option_c_img', 'option_d_img', 'option_e_img']:
            if question.get(file_field):
                try:
                    os.remove(os.path.join('static/uploads', question[file_field]))
                except:
                    pass
        
        BankQuestionModel.delete(question_id)
        flash("Pertanyaan berhasil dihapus dari bank soal.")
    except Exception as e:
        flash(f"Gagal menghapus pertanyaan: {str(e)}")
    
    return redirect(url_for('question_bank.view_bank', bank_id=question['bank_id']))


# ============== USE BANK IN QUIZ/ASSIGNMENT ==============

@question_bank_bp.route('/<int:bank_id>/use-in-quiz', defaults={'class_id': 0}, methods=['GET', 'POST'])
@question_bank_bp.route('/<int:bank_id>/use-in-quiz/<int:class_id>', methods=['GET', 'POST'])
@login_required
@teacher_required
def use_bank_in_quiz(bank_id, class_id):
    """Gunakan bank soal untuk membuat quiz di kelas lain"""
    bank = QuestionBankModel.get_by_id(bank_id)
    if not bank:
        flash("Bank soal tidak ditemukan.")
        return redirect(url_for('question_bank.index'))
    
    # Check access
    if bank['created_by'] != session.get('user_id'):
        flash("Anda tidak memiliki akses ke bank soal ini.")
        return redirect(url_for('question_bank.index'))

    from models.class_model import ClassModel
    classes = ClassModel.get_all()
    selected_class_id = class_id if class_id else session.get('selected_class_id')
    
    questions = BankQuestionModel.get_by_bank(bank_id)
    if not questions:
        flash("Bank soal ini tidak memiliki pertanyaan.")
        return redirect(url_for('question_bank.view_bank', bank_id=bank_id))
    
    if request.method == 'POST':
        # Ambil pilihan kelas dari form jika belum ada
        try:
            selected_class_id = int(request.form.get('class_id') or selected_class_id or 0)
        except:
            selected_class_id = 0

        if not selected_class_id:
            flash("Pilih kelas tujuan terlebih dahulu.")
            return render_template('teacher/question_bank/use_in_quiz.html', 
                                 bank=bank, questions=questions, class_id=selected_class_id,
                                 classes=classes, selected_class_id=selected_class_id)

        quiz_title = request.form.get('quiz_title', '').strip()
        due_at = request.form.get('due_at') or None
        attempt_limit = request.form.get('attempt_limit') or None
        duration_minutes = request.form.get('duration_minutes') or None
        num_options = request.form.get('num_options', '5')
        selected_questions = request.form.getlist('selected_questions')
        
        # Validasi
        if not quiz_title:
            flash("Judul kuis tidak boleh kosong.")
            return render_template('teacher/question_bank/use_in_quiz.html', 
                                 bank=bank, questions=questions, class_id=selected_class_id,
                                 classes=classes, selected_class_id=selected_class_id)
        
        if not selected_questions:
            flash("Pilih minimal satu pertanyaan.")
            return render_template('teacher/question_bank/use_in_quiz.html', 
                                 bank=bank, questions=questions, class_id=selected_class_id,
                                 classes=classes, selected_class_id=selected_class_id)
        
        # Parse integers
        if attempt_limit:
            try:
                attempt_limit = int(attempt_limit)
                if attempt_limit <= 0:
                    raise ValueError()
            except:
                flash("Batas percobaan harus berupa angka positif.")
                return render_template('teacher/question_bank/use_in_quiz.html', 
                                     bank=bank, questions=questions, class_id=selected_class_id,
                                     classes=classes, selected_class_id=selected_class_id)
        
        if duration_minutes:
            try:
                duration_minutes = int(duration_minutes)
                if duration_minutes <= 0:
                    raise ValueError()
            except:
                flash("Durasi harus berupa angka positif.")
                return render_template('teacher/question_bank/use_in_quiz.html', 
                                     bank=bank, questions=questions, class_id=selected_class_id,
                                     classes=classes, selected_class_id=selected_class_id)
        
        try:
            num_options = int(num_options)
            if num_options < 2 or num_options > 5:
                num_options = 5
        except:
            num_options = 5
        
        if due_at:
            try:
                due_at = datetime.strptime(due_at, '%Y-%m-%dT%H:%M')
            except:
                flash("Format tanggal tidak valid.")
                return render_template('teacher/question_bank/use_in_quiz.html', 
                                     bank=bank, questions=questions, class_id=selected_class_id,
                                     classes=classes, selected_class_id=selected_class_id)
        
        try:
            # Create quiz
            quiz_id = QuizModel.create(quiz_title, selected_class_id, session.get('user_id'), 
                                      due_at, attempt_limit, duration_minutes, num_options)
            
            # Copy selected questions from bank to quiz
            for q_id in selected_questions:
                try:
                    BankQuestionModel.copy_to_quiz(int(q_id), quiz_id, bank_id)
                except:
                    pass
            
            flash(f"Kuis '{quiz_title}' berhasil dibuat dari bank soal '{bank['name']}'!")
            return redirect(url_for('teacher.dashboard'))
        except Exception as e:
            flash(f"Gagal membuat kuis: {str(e)}")
    
    return render_template('teacher/question_bank/use_in_quiz.html', 
                         bank=bank, questions=questions, class_id=selected_class_id,
                         classes=classes, selected_class_id=selected_class_id)


# ============== ASSIGNMENT BANK MANAGEMENT ==============

@question_bank_bp.route('/assignment/')
@login_required
@teacher_required
def assignment_banks_index():
    """Lihat daftar bank tugas"""
    teacher_id = session.get('user_id')
    banks = AssignmentBankModel.get_by_teacher(teacher_id)
    return render_template('teacher/question_bank/assignment_banks_index.html', banks=banks)

@question_bank_bp.route('/assignment/create', methods=['GET', 'POST'])
@login_required
@teacher_required
def create_assignment_bank():
    """Buat bank tugas baru"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        content = request.form.get('content', '').strip()
        file_path = None
        
        if not name:
            flash("Nama bank tugas tidak boleh kosong.")
            return render_template('teacher/question_bank/create_assignment_bank.html')
        
        # Handle file upload
        if 'file' in request.files and request.files['file'].filename:
            try:
                file_path = save_uploaded_file(request.files['file'], 'assignment')
            except Exception as e:
                flash(f"Gagal upload file: {str(e)}")
                return render_template('teacher/question_bank/create_assignment_bank.html')
        
        try:
            bank_id = AssignmentBankModel.create(name, session.get('user_id'), 
                                                content, description, file_path)
            flash(f"Bank tugas '{name}' berhasil dibuat.")
            return redirect(url_for('question_bank.assignment_banks_index'))
        except Exception as e:
            flash(f"Gagal membuat bank tugas: {str(e)}")
    
    return render_template('teacher/question_bank/create_assignment_bank.html')

@question_bank_bp.route('/assignment/<int:bank_id>/edit', methods=['GET', 'POST'])
@login_required
@teacher_required
def edit_assignment_bank(bank_id):
    """Edit bank tugas"""
    bank = AssignmentBankModel.get_by_id(bank_id)
    if not bank:
        flash("Bank tugas tidak ditemukan.")
        return redirect(url_for('question_bank.assignment_banks_index'))
    
    # Check access
    if bank['created_by'] != session.get('user_id'):
        flash("Anda tidak memiliki akses ke bank tugas ini.")
        return redirect(url_for('question_bank.assignment_banks_index'))
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        content = request.form.get('content', '').strip()
        file_path = bank.get('file_path')
        
        if not name:
            flash("Nama bank tugas tidak boleh kosong.")
            return render_template('teacher/question_bank/edit_assignment_bank.html', bank=bank)
        
        # Handle file upload
        if 'file' in request.files and request.files['file'].filename:
            try:
                # Delete old file if exists
                if file_path:
                    old_path = os.path.join('static/uploads', file_path)
                    if os.path.exists(old_path):
                        try:
                            os.remove(old_path)
                        except:
                            pass
                file_path = save_uploaded_file(request.files['file'], 'assignment')
            except Exception as e:
                flash(f"Gagal upload file: {str(e)}")
                return render_template('teacher/question_bank/edit_assignment_bank.html', bank=bank)
        
        try:
            AssignmentBankModel.update(bank_id, name, content, description, file_path)
            flash("Bank tugas berhasil diperbarui.")
            return redirect(url_for('question_bank.assignment_banks_index'))
        except Exception as e:
            flash(f"Gagal memperbarui bank tugas: {str(e)}")
    
    return render_template('teacher/question_bank/edit_assignment_bank.html', bank=bank)

@question_bank_bp.route('/assignment/<int:bank_id>/delete')
@login_required
@teacher_required
def delete_assignment_bank(bank_id):
    """Hapus bank tugas"""
    bank = AssignmentBankModel.get_by_id(bank_id)
    if not bank:
        flash("Bank tugas tidak ditemukan.")
        return redirect(url_for('question_bank.assignment_banks_index'))
    
    # Check access
    if bank['created_by'] != session.get('user_id'):
        flash("Anda tidak memiliki akses ke bank tugas ini.")
        return redirect(url_for('question_bank.assignment_banks_index'))
    
    try:
        # Delete file if exists
        if bank.get('file_path'):
            try:
                os.remove(os.path.join('static/uploads', bank['file_path']))
            except:
                pass
        
        AssignmentBankModel.delete(bank_id)
        flash("Bank tugas berhasil dihapus.")
    except Exception as e:
        flash(f"Gagal menghapus bank tugas: {str(e)}")
    
    return redirect(url_for('question_bank.assignment_banks_index'))

@question_bank_bp.route('/assignment/<int:bank_id>/use', defaults={'class_id': 0}, methods=['GET', 'POST'])
@question_bank_bp.route('/assignment/<int:bank_id>/use/<int:class_id>', methods=['GET', 'POST'])
@login_required
@teacher_required
def use_assignment_bank(bank_id, class_id):
    """Gunakan bank tugas untuk membuat assignment di kelas lain"""
    bank = AssignmentBankModel.get_by_id(bank_id)
    if not bank:
        flash("Bank tugas tidak ditemukan.")
        return redirect(url_for('question_bank.assignment_banks_index'))
    
    # Check access
    if bank['created_by'] != session.get('user_id'):
        flash("Anda tidak memiliki akses ke bank tugas ini.")
        return redirect(url_for('question_bank.assignment_banks_index'))

    from models.class_model import ClassModel
    classes = ClassModel.get_all()
    selected_class_id = class_id if class_id else session.get('selected_class_id')
    
    if request.method == 'POST':
        try:
            selected_class_id = int(request.form.get('class_id') or selected_class_id or 0)
        except:
            selected_class_id = 0

        task_title = request.form.get('task_title', '').strip()
        due_date = request.form.get('due_date') or None
        
        if not selected_class_id:
            flash("Pilih kelas tujuan terlebih dahulu.")
            return render_template('teacher/question_bank/use_assignment_bank.html', 
                                 bank=bank, class_id=selected_class_id, classes=classes,
                                 selected_class_id=selected_class_id)

        if not task_title:
            flash("Judul tugas tidak boleh kosong.")
            return render_template('teacher/question_bank/use_assignment_bank.html', 
                                 bank=bank, class_id=selected_class_id, classes=classes,
                                 selected_class_id=selected_class_id)
        
        if due_date:
            try:
                due_date = datetime.strptime(due_date, '%Y-%m-%d')
            except:
                flash("Format tanggal tidak valid.")
                return render_template('teacher/question_bank/use_assignment_bank.html', 
                                     bank=bank, class_id=selected_class_id, classes=classes,
                                     selected_class_id=selected_class_id)
        
        try:
            # Create assignment from bank
            task_id = AssignmentModel.create(task_title, bank['content'], selected_class_id, 
                                            session.get('user_id'), due_date, bank['file_path'])
            
            # Track the relationship
            AssignmentBankModel.copy_to_assignment(bank_id, task_id)
            
            flash(f"Tugas '{task_title}' berhasil dibuat dari bank tugas '{bank['name']}'!")
            return redirect(url_for('teacher.dashboard'))
        except Exception as e:
            flash(f"Gagal membuat tugas: {str(e)}")
    
    return render_template('teacher/question_bank/use_assignment_bank.html', 
                         bank=bank, class_id=selected_class_id, classes=classes,
                         selected_class_id=selected_class_id)


# ============== MATERIAL BANK MANAGEMENT ==============

@question_bank_bp.route('/material/')
@login_required
@teacher_required
def material_banks_index():
    """Lihat daftar bank materi"""
    teacher_id = session.get('user_id')
    banks = MaterialBankModel.get_by_teacher(teacher_id)
    return render_template('teacher/question_bank/material_banks_index.html', banks=banks)

@question_bank_bp.route('/material/create', methods=['GET', 'POST'])
@login_required
@teacher_required
def create_material_bank():
    """Buat bank materi baru"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        content = request.form.get('content', '').strip()
        file_path = None

        if not name:
            flash("Nama bank materi tidak boleh kosong.")
            return render_template('teacher/question_bank/create_material_bank.html')

        upload = request.files.get('file')
        if upload and upload.filename:
            if not allowed_file(upload.filename):
                flash("Format file tidak diizinkan.")
                return render_template('teacher/question_bank/create_material_bank.html')
            try:
                file_path = save_uploaded_file(upload, 'material_bank')
            except Exception as e:
                flash(f"Gagal upload file: {str(e)}")
                return render_template('teacher/question_bank/create_material_bank.html')

        try:
            MaterialBankModel.create(name, session.get('user_id'), content, description, file_path)
            flash(f"Bank materi '{name}' berhasil dibuat.")
            return redirect(url_for('question_bank.material_banks_index'))
        except Exception as e:
            flash(f"Gagal membuat bank materi: {str(e)}")

    return render_template('teacher/question_bank/create_material_bank.html')

@question_bank_bp.route('/material/<int:bank_id>/edit', methods=['GET', 'POST'])
@login_required
@teacher_required
def edit_material_bank(bank_id):
    """Edit bank materi"""
    bank = MaterialBankModel.get_by_id(bank_id)
    if not bank:
        flash("Bank materi tidak ditemukan.")
        return redirect(url_for('question_bank.material_banks_index'))
    
    # Check access
    if bank['created_by'] != session.get('user_id'):
        flash("Anda tidak memiliki akses ke bank materi ini.")
        return redirect(url_for('question_bank.material_banks_index'))
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        content = request.form.get('content', '').strip()
        file_path = bank.get('file_path')
        
        if not name:
            flash("Nama bank materi tidak boleh kosong.")
            return render_template('teacher/question_bank/edit_material_bank.html', bank=bank)
        
        # Handle file upload
        if 'file' in request.files and request.files['file'].filename:
            try:
                # Delete old file if exists
                if file_path:
                    old_path = os.path.join('static/uploads', file_path)
                    if os.path.exists(old_path):
                        try:
                            os.remove(old_path)
                        except:
                            pass
                file_path = save_uploaded_file(request.files['file'], 'material_bank')
            except Exception as e:
                flash(f"Gagal upload file: {str(e)}")
                return render_template('teacher/question_bank/edit_material_bank.html', bank=bank)
        
        try:
            MaterialBankModel.update(bank_id, name, content, description, file_path)
            flash("Bank materi berhasil diperbarui.")
            return redirect(url_for('question_bank.material_banks_index'))
        except Exception as e:
            flash(f"Gagal memperbarui bank materi: {str(e)}")
    
    return render_template('teacher/question_bank/edit_material_bank.html', bank=bank)

@question_bank_bp.route('/material/<int:bank_id>/delete')
@login_required
@teacher_required
def delete_material_bank(bank_id):
    """Hapus bank materi"""
    bank = MaterialBankModel.get_by_id(bank_id)
    if not bank:
        flash("Bank materi tidak ditemukan.")
        return redirect(url_for('question_bank.material_banks_index'))
    
    # Check access
    if bank['created_by'] != session.get('user_id'):
        flash("Anda tidak memiliki akses ke bank materi ini.")
        return redirect(url_for('question_bank.material_banks_index'))
    
    try:
        # Delete file if exists
        if bank.get('file_path'):
            try:
                os.remove(os.path.join('static/uploads', bank['file_path']))
            except:
                pass
        
        MaterialBankModel.delete(bank_id)
        flash("Bank materi berhasil dihapus.")
    except Exception as e:
        flash(f"Gagal menghapus bank materi: {str(e)}")
    
    return redirect(url_for('question_bank.material_banks_index'))

@question_bank_bp.route('/material/<int:bank_id>/use', defaults={'class_id': 0}, methods=['GET', 'POST'])
@question_bank_bp.route('/material/<int:bank_id>/use/<int:class_id>', methods=['GET', 'POST'])
@login_required
@teacher_required
def use_material_bank(bank_id, class_id):
    """Gunakan bank materi untuk membuat materi di kelas lain"""
    bank = MaterialBankModel.get_by_id(bank_id)
    if not bank:
        flash("Bank materi tidak ditemukan.")
        return redirect(url_for('question_bank.material_banks_index'))

    if bank['created_by'] != session.get('user_id'):
        flash("Anda tidak memiliki akses ke bank materi ini.")
        return redirect(url_for('question_bank.material_banks_index'))

    from models.class_model import ClassModel
    classes = ClassModel.get_all()

    selected_class_id = class_id if class_id else session.get('selected_class_id')
    if selected_class_id == 0:
        selected_class_id = session.get('selected_class_id')

    if request.method == 'POST':
        try:
            selected_class_id = int(request.form.get('class_id') or 0)
        except:
            selected_class_id = 0

        if not selected_class_id:
            flash("Pilih kelas tujuan terlebih dahulu.")
            return render_template('teacher/question_bank/use_material_bank.html', 
                                 bank=bank, classes=classes, selected_class_id=selected_class_id)

        try:
            MaterialBankModel.copy_to_class(bank_id, selected_class_id, session.get('user_id'))
            flash(f"Materi berhasil dibuat di kelas terpilih dari bank '{bank['name']}'.")
            return redirect(url_for('teacher.dashboard'))
        except Exception as e:
            flash(f"Gagal menggunakan bank materi: {str(e)}")

    return render_template('teacher/question_bank/use_material_bank.html', 
                         bank=bank, classes=classes, selected_class_id=selected_class_id)