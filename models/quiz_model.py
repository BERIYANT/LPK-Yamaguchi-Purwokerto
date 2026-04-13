from utils.database import get_db
from datetime import datetime

class QuizModel:
    @staticmethod
    def create(title, class_id, created_by, due_at=None, attempt_limit=None, duration_minutes=None, num_options=5):
        db = get_db()
        cur = db.cursor()
        try:
            # Try insert with new columns
            cur.execute(
                "INSERT INTO quizzes (title, class_id, created_by, created_at, due_at, attempt_limit, duration_minutes, num_options) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (title, class_id, created_by, datetime.now(), due_at, attempt_limit, duration_minutes, num_options)
            )
        except Exception:
            # Fallback insert without new columns
            cur.execute(
                "INSERT INTO quizzes (title, class_id, created_by, created_at) VALUES (%s, %s, %s, %s)",
                (title, class_id, created_by, datetime.now())
            )
        db.commit()
        quiz_id = cur.lastrowid

        # Post-insert: if optional fields are provided, try to update them (safe if columns exist)
        try:
            if due_at is not None or attempt_limit is not None or duration_minutes is not None or num_options != 5:
                cur.execute(
                    "UPDATE quizzes SET due_at=%s, attempt_limit=%s, duration_minutes=%s, num_options=%s WHERE id=%s",
                    (due_at, attempt_limit, duration_minutes, num_options, quiz_id)
                )
                db.commit()
        except Exception:
            # Column(s) may not exist yet; ignore
            pass

        cur.close()
        return quiz_id

    @staticmethod
    def get_by_id(quiz_id):
        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT * FROM quizzes WHERE id=%s", (quiz_id,))
        quiz = cur.fetchone()
        cur.close()
        return quiz

    @staticmethod
    def get_by_class(class_id):
        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT * FROM quizzes WHERE class_id=%s ORDER BY created_at DESC", (class_id,))
        quizzes = cur.fetchall()
        cur.close()
        return quizzes

    @staticmethod
    def update(quiz_id, title, due_at=None, attempt_limit=None, duration_minutes=None, num_options=5):
        db = get_db()
        cur = db.cursor()
        try:
            # Update with new columns
            cur.execute(
                "UPDATE quizzes SET title=%s, due_at=%s, attempt_limit=%s, duration_minutes=%s, num_options=%s WHERE id=%s",
                (title, due_at, attempt_limit, duration_minutes, num_options, quiz_id)
            )
        except Exception:
            # Fallback to legacy update
            cur.execute(
                "UPDATE quizzes SET title=%s WHERE id=%s",
                (title, quiz_id)
            )
        db.commit()
        cur.close()

    @staticmethod
    def delete(quiz_id):
        db = get_db()
        cur = db.cursor()
        cur.execute("DELETE FROM quizzes WHERE id=%s", (quiz_id,))
        db.commit()
        cur.close()

class QuizQuestionModel:
    @staticmethod
    def create(quiz_id, question, option_a, option_b, option_c, option_d, option_e, correct_option, image_path=None,
             option_a_img=None, option_b_img=None, option_c_img=None, option_d_img=None, option_e_img=None, audio_path=None):
        db = get_db()
        cur = db.cursor()
        cur.execute(
            """INSERT INTO quiz_questions 
             (quiz_id, question, image_path, audio_path,
             option_a, option_b, option_c, option_d, option_e, correct_option,
             option_a_img, option_b_img, option_c_img, option_d_img, option_e_img) 
             VALUES (%s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s)""",
             (quiz_id, question, image_path, audio_path,
             option_a, option_b, option_c, option_d, option_e, correct_option,
             option_a_img, option_b_img, option_c_img, option_d_img, option_e_img)
        )
        db.commit()
        question_id = cur.lastrowid
        cur.close()
        return question_id

    @staticmethod
    def get_by_quiz(quiz_id):
        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT * FROM quiz_questions WHERE quiz_id=%s ORDER BY id", (quiz_id,))
        questions = cur.fetchall()
        cur.close()
        return questions

    @staticmethod
    def get_by_id(question_id):
        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT * FROM quiz_questions WHERE id=%s", (question_id,))
        question = cur.fetchone()
        cur.close()
        return question

    @staticmethod
    def update(question_id, question, option_a, option_b, option_c, option_d, option_e, correct_option, image_path=None,
                   option_a_img=None, option_b_img=None, option_c_img=None, option_d_img=None, option_e_img=None, audio_path=None):
        db = get_db()
        cur = db.cursor()
        if image_path is not None or audio_path is not None or any(v is not None for v in [option_a_img, option_b_img, option_c_img, option_d_img, option_e_img]):
            cur.execute(
                """UPDATE quiz_questions 
                SET question=%s, 
                        image_path=%s,
                        audio_path=%s,
                    option_a=%s, option_b=%s, option_c=%s, option_d=%s, option_e=%s, 
                    correct_option=%s,
                    option_a_img=%s, option_b_img=%s, option_c_img=%s, option_d_img=%s, option_e_img=%s
                WHERE id=%s""",
                    (question, image_path, audio_path, option_a, option_b, option_c, option_d, option_e, correct_option,
                 option_a_img, option_b_img, option_c_img, option_d_img, option_e_img, question_id)
            )
        else:
            cur.execute(
                """UPDATE quiz_questions 
                SET question=%s, 
                    option_a=%s, option_b=%s, option_c=%s, option_d=%s, option_e=%s, 
                    correct_option=%s
                WHERE id=%s""",
                (question, option_a, option_b, option_c, option_d, option_e, correct_option, question_id)
            )
        db.commit()
        cur.close()

    @staticmethod
    def delete(question_id):
        db = get_db()
        cur = db.cursor()
        cur.execute("DELETE FROM quiz_questions WHERE id=%s", (question_id,))
        db.commit()
        cur.close()