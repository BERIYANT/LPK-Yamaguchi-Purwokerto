from utils.database import get_db
from datetime import datetime

class QuestionBankModel:
    """Model untuk mengelola question bank (bank soal)"""
    
    @staticmethod
    def create(name, created_by, description=None):
        """Membuat question bank baru"""
        db = get_db()
        cur = db.cursor()
        cur.execute(
            """INSERT INTO question_banks (name, description, created_by, created_at) 
            VALUES (%s, %s, %s, %s)""",
            (name, description, created_by, datetime.now())
        )
        db.commit()
        bank_id = cur.lastrowid
        cur.close()
        return bank_id
    
    @staticmethod
    def get_by_id(bank_id):
        """Mendapatkan bank soal berdasarkan ID"""
        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT * FROM question_banks WHERE id=%s", (bank_id,))
        bank = cur.fetchone()
        cur.close()
        return bank
    
    @staticmethod
    def get_by_teacher(teacher_id):
        """Mendapatkan semua bank soal yang dibuat guru"""
        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute(
            """SELECT qb.*, COUNT(bq.id) as question_count 
            FROM question_banks qb 
            LEFT JOIN bank_questions bq ON qb.id = bq.bank_id
            WHERE qb.created_by=%s 
            GROUP BY qb.id
            ORDER BY qb.created_at DESC""",
            (teacher_id,)
        )
        banks = cur.fetchall()
        cur.close()
        return banks
    
    @staticmethod
    def update(bank_id, name, description=None):
        """Update information bank soal"""
        db = get_db()
        cur = db.cursor()
        cur.execute(
            """UPDATE question_banks 
            SET name=%s, description=%s, updated_at=%s 
            WHERE id=%s""",
            (name, description, datetime.now(), bank_id)
        )
        db.commit()
        cur.close()
    
    @staticmethod
    def delete(bank_id):
        """Menghapus bank soal (cascade delete untuk semua questions)"""
        db = get_db()
        cur = db.cursor()
        cur.execute("DELETE FROM question_banks WHERE id=%s", (bank_id,))
        db.commit()
        cur.close()


class BankQuestionModel:
    """Model untuk mengelola questions dalam bank"""
    
    @staticmethod
    def create(bank_id, question, option_a, option_b, option_c, option_d, option_e, 
               correct_option, image_path=None, option_a_img=None, option_b_img=None, 
               option_c_img=None, option_d_img=None, option_e_img=None, audio_path=None):
        """Membuat question baru di dalam bank"""
        db = get_db()
        cur = db.cursor()
        cur.execute(
            """INSERT INTO bank_questions 
             (bank_id, question, image_path, audio_path,
             option_a, option_b, option_c, option_d, option_e, correct_option,
             option_a_img, option_b_img, option_c_img, option_d_img, option_e_img) 
             VALUES (%s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s)""",
            (bank_id, question, image_path, audio_path,
             option_a, option_b, option_c, option_d, option_e, correct_option,
             option_a_img, option_b_img, option_c_img, option_d_img, option_e_img)
        )
        db.commit()
        question_id = cur.lastrowid
        cur.close()
        return question_id
    
    @staticmethod
    def get_by_id(question_id):
        """Mendapatkan soal berdasarkan ID"""
        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT * FROM bank_questions WHERE id=%s", (question_id,))
        question = cur.fetchone()
        cur.close()
        return question
    
    @staticmethod
    def get_by_bank(bank_id):
        """Mendapatkan semua soal dalam bank"""
        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT * FROM bank_questions WHERE bank_id=%s ORDER BY id", (bank_id,))
        questions = cur.fetchall()
        cur.close()
        return questions
    
    @staticmethod
    def update(question_id, question, option_a, option_b, option_c, option_d, option_e, 
               correct_option, image_path=None, option_a_img=None, option_b_img=None, 
               option_c_img=None, option_d_img=None, option_e_img=None, audio_path=None):
        """Update soal"""
        db = get_db()
        cur = db.cursor()
        cur.execute(
            """UPDATE bank_questions 
             SET question=%s, image_path=%s, audio_path=%s,
                 option_a=%s, option_b=%s, option_c=%s, option_d=%s, option_e=%s, correct_option=%s,
                 option_a_img=%s, option_b_img=%s, option_c_img=%s, option_d_img=%s, option_e_img=%s
             WHERE id=%s""",
            (question, image_path, audio_path,
             option_a, option_b, option_c, option_d, option_e, correct_option,
             option_a_img, option_b_img, option_c_img, option_d_img, option_e_img, question_id)
        )
        db.commit()
        cur.close()
    
    @staticmethod
    def delete(question_id):
        """Menghapus soal dari bank"""
        db = get_db()
        cur = db.cursor()
        cur.execute("DELETE FROM bank_questions WHERE id=%s", (question_id,))
        db.commit()
        cur.close()
    
    @staticmethod
    def copy_to_quiz(bank_question_id, quiz_id, source_bank_id):
        """Copy soal dari bank ke quiz"""
        db = get_db()
        cur = db.cursor()
        
        # Get question details
        bank_question = BankQuestionModel.get_by_id(bank_question_id)
        if not bank_question:
            cur.close()
            return None
        
        # Create quiz question from bank question
        from models.quiz_model import QuizQuestionModel
        question_id = QuizQuestionModel.create(
            quiz_id=quiz_id,
            question=bank_question['question'],
            option_a=bank_question['option_a'],
            option_b=bank_question['option_b'],
            option_c=bank_question['option_c'],
            option_d=bank_question['option_d'],
            option_e=bank_question['option_e'],
            correct_option=bank_question['correct_option'],
            image_path=bank_question['image_path'],
            option_a_img=bank_question['option_a_img'],
            option_b_img=bank_question['option_b_img'],
            option_c_img=bank_question['option_c_img'],
            option_d_img=bank_question['option_d_img'],
            option_e_img=bank_question['option_e_img'],
            audio_path=bank_question['audio_path']
        )
        
        # Track relationship
        cur.execute(
            """INSERT INTO quiz_from_bank 
             (quiz_id, bank_question_id, source_bank_id) 
             VALUES (%s, %s, %s)""",
            (quiz_id, bank_question_id, source_bank_id)
        )
        db.commit()
        cur.close()
        return question_id


class AssignmentBankModel:
    """Model untuk mengelola assignment bank (bank tugas)"""
    
    @staticmethod
    def create(name, created_by, content=None, description=None, file_path=None):
        """Membuat assignment bank baru"""
        db = get_db()
        cur = db.cursor()
        cur.execute(
            """INSERT INTO assignment_banks 
            (name, description, content, file_path, created_by, created_at) 
            VALUES (%s, %s, %s, %s, %s, %s)""",
            (name, description, content, file_path, created_by, datetime.now())
        )
        db.commit()
        bank_id = cur.lastrowid
        cur.close()
        return bank_id
    
    @staticmethod
    def get_by_id(bank_id):
        """Mendapatkan assignment bank berdasarkan ID"""
        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT * FROM assignment_banks WHERE id=%s", (bank_id,))
        bank = cur.fetchone()
        cur.close()
        return bank
    
    @staticmethod
    def get_by_teacher(teacher_id):
        """Mendapatkan semua assignment bank yang dibuat guru"""
        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute(
            """SELECT ab.* FROM assignment_banks ab 
            WHERE ab.created_by=%s 
            ORDER BY ab.created_at DESC""",
            (teacher_id,)
        )
        banks = cur.fetchall()
        cur.close()
        return banks
    
    @staticmethod
    def update(bank_id, name, content=None, description=None, file_path=None):
        """Update assignment bank"""
        db = get_db()
        cur = db.cursor()
        cur.execute(
            """UPDATE assignment_banks 
            SET name=%s, description=%s, content=%s, file_path=%s, updated_at=%s 
            WHERE id=%s""",
            (name, description, content, file_path, datetime.now(), bank_id)
        )
        db.commit()
        cur.close()
    
    @staticmethod
    def delete(bank_id):
        """Menghapus assignment bank"""
        db = get_db()
        cur = db.cursor()
        cur.execute("DELETE FROM assignment_banks WHERE id=%s", (bank_id,))
        db.commit()
        cur.close()
    
    @staticmethod
    def copy_to_assignment(bank_id, task_id):
        """Copy assignment dari bank ke kelas baru"""
        db = get_db()
        cur = db.cursor()
        
        # Track relationship
        cur.execute(
            """INSERT INTO assignment_from_bank 
             (task_id, bank_assignment_id) 
             VALUES (%s, %s)""",
            (task_id, bank_id)
        )
        db.commit()
        cur.close()


class MaterialBankModel:
    """Model untuk mengelola bank materi pembelajaran"""

    @staticmethod
    def create(name, created_by, content=None, description=None, file_path=None):
        """Membuat bank materi baru"""
        db = get_db()
        cur = db.cursor()
        cur.execute(
            """INSERT INTO material_banks 
            (name, description, content, file_path, created_by, created_at) 
            VALUES (%s, %s, %s, %s, %s, %s)""",
            (name, description, content, file_path, created_by, datetime.now())
        )
        db.commit()
        bank_id = cur.lastrowid
        cur.close()
        return bank_id

    @staticmethod
    def get_by_id(bank_id):
        """Mendapatkan bank materi berdasarkan ID"""
        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT * FROM material_banks WHERE id=%s", (bank_id,))
        bank = cur.fetchone()
        cur.close()
        return bank

    @staticmethod
    def get_by_teacher(teacher_id):
        """Mendapatkan semua bank materi yang dibuat guru"""
        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute(
            """SELECT mb.* FROM material_banks mb 
            WHERE mb.created_by=%s 
            ORDER BY mb.created_at DESC""",
            (teacher_id,)
        )
        banks = cur.fetchall()
        cur.close()
        return banks

    @staticmethod
    def update(bank_id, name, content=None, description=None, file_path=None):
        """Update bank materi"""
        db = get_db()
        cur = db.cursor()
        cur.execute(
            """UPDATE material_banks 
            SET name=%s, description=%s, content=%s, file_path=%s, updated_at=%s 
            WHERE id=%s""",
            (name, description, content, file_path, datetime.now(), bank_id)
        )
        db.commit()
        cur.close()

    @staticmethod
    def delete(bank_id):
        """Menghapus bank materi"""
        db = get_db()
        cur = db.cursor()
        cur.execute("DELETE FROM material_banks WHERE id=%s", (bank_id,))
        db.commit()
        cur.close()

    @staticmethod
    def copy_to_class(bank_id, class_id, created_by):
        """Copy materi dari bank ke kelas baru"""
        bank = MaterialBankModel.get_by_id(bank_id)
        if not bank:
            return None

        from models.material_model import MaterialModel

        # Buat materi baru di kelas tujuan
        material_id = MaterialModel.create(
            title=bank['name'],
            content=bank.get('content') or '',
            class_id=class_id,
            created_by=created_by,
            file_path=bank.get('file_path')
        )

        # Track relationship
        db = get_db()
        cur = db.cursor()
        cur.execute(
            """INSERT INTO material_from_bank 
             (material_id, bank_material_id) 
             VALUES (%s, %s)""",
            (material_id, bank_id)
        )
        db.commit()
        cur.close()
        return material_id
