from utils.database import get_db
from datetime import datetime

class AssignmentModel:
    @staticmethod
    def create(title, description, class_id, created_by, due_date=None, file_path=None):
        db = get_db()
        cur = db.cursor()
        cur.execute(
            """INSERT INTO tasks (title, description, due_date, file_path, class_id, created_by, created_at) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (title, description, due_date, file_path, class_id, created_by, datetime.now())
        )
        db.commit()
        task_id = cur.lastrowid
        cur.close()
        return task_id

    @staticmethod
    def get_by_id(task_id):
        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT * FROM tasks WHERE id=%s", (task_id,))
        task = cur.fetchone()
        cur.close()
        return task

    @staticmethod
    def get_by_class(class_id):
        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT * FROM tasks WHERE class_id=%s ORDER BY created_at DESC", (class_id,))
        tasks = cur.fetchall()
        cur.close()
        return tasks

    @staticmethod
    def update(task_id, title, description, due_date=None, file_path=None):
        db = get_db()
        cur = db.cursor()
        if file_path is not None:
            cur.execute(
                "UPDATE tasks SET title=%s, description=%s, due_date=%s, file_path=%s WHERE id=%s",
                (title, description, due_date, file_path, task_id)
            )
        else:
            cur.execute(
                "UPDATE tasks SET title=%s, description=%s, due_date=%s WHERE id=%s",
                (title, description, due_date, task_id)
            )
        db.commit()
        cur.close()

    @staticmethod
    def delete(task_id):
        db = get_db()
        cur = db.cursor()
        cur.execute("DELETE FROM tasks WHERE id=%s", (task_id,))
        db.commit()
        cur.close()

class AssignmentSubmissionModel:
    @staticmethod
    def create(task_id, student_id, file_path):
        db = get_db()
        cur = db.cursor()
        cur.execute(
            "INSERT INTO task_submissions (task_id, student_id, file_path, submitted_at) VALUES (%s, %s, %s, %s)",
            (task_id, student_id, file_path, datetime.now())
        )
        db.commit()
        submission_id = cur.lastrowid
        cur.close()
        return submission_id

    @staticmethod
    def get_by_task_and_student(task_id, student_id):
        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute(
            "SELECT * FROM task_submissions WHERE task_id=%s AND student_id=%s ORDER BY submitted_at DESC LIMIT 1",
            (task_id, student_id)
        )
        submission = cur.fetchone()
        cur.close()
        return submission

    @staticmethod
    def get_by_task(task_id):
        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute(
            """SELECT ts.*, u.username, u.full_name 
            FROM task_submissions ts 
            JOIN users u ON ts.student_id = u.id 
            WHERE ts.task_id=%s 
            ORDER BY ts.submitted_at DESC""",
            (task_id,)
        )
        submissions = cur.fetchall()
        cur.close()
        return submissions

    @staticmethod
    def update_grade(submission_id, score, feedback, graded_by):
        db = get_db()
        cur = db.cursor()
        cur.execute(
            "UPDATE task_submissions SET score=%s, feedback=%s, graded_by=%s, graded_at=%s WHERE id=%s",
            (score, feedback, graded_by, datetime.now(), submission_id)
        )
        db.commit()
        cur.close()

    @staticmethod
    def get_student_submissions(student_id):
        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute(
            """SELECT ts.*, t.title as task_title, t.due_date, u.full_name as graded_by_name
            FROM task_submissions ts
            JOIN tasks t ON ts.task_id = t.id
            LEFT JOIN users u ON ts.graded_by = u.id
            WHERE ts.student_id = %s
            ORDER BY ts.submitted_at DESC""",
            (student_id,)
        )
        submissions = cur.fetchall()
        cur.close()
        return submissions