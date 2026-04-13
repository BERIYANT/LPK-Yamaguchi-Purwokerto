from utils.database import get_db

class ClassModel:
    @staticmethod
    def get_all():
        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT * FROM classes ORDER BY name")
        classes = cur.fetchall()
        cur.close()
        return classes

    @staticmethod
    def get_by_id(class_id):
        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT * FROM classes WHERE id=%s", (class_id,))
        class_data = cur.fetchone()
        cur.close()
        return class_data

    @staticmethod
    def create(name, schedule=None, description=None, start_time=None, end_time=None):
        db = get_db()
        cur = db.cursor()
        cur.execute(
            "INSERT INTO classes (name, schedule, description, start_time, end_time) VALUES (%s, %s, %s, %s, %s)",
            (name, schedule, description, start_time, end_time)
        )
        db.commit()
        class_id = cur.lastrowid
        cur.close()
        return class_id

    @staticmethod
    def update(class_id, name, schedule=None, description=None, start_time=None, end_time=None):
        db = get_db()
        cur = db.cursor()
        cur.execute(
            "UPDATE classes SET name=%s, schedule=%s, description=%s, start_time=%s, end_time=%s WHERE id=%s",
            (name, schedule, description, start_time, end_time, class_id)
        )
        db.commit()
        cur.close()

    @staticmethod
    def delete(class_id):
        db = get_db()
        cur = db.cursor()
        cur.execute("DELETE FROM classes WHERE id=%s", (class_id,))
        db.commit()
        cur.close()

    @staticmethod
    def get_students_count(class_id):
        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT COUNT(*) as count FROM enrollments WHERE class_id=%s", (class_id,))
        result = cur.fetchone()
        cur.close()
        return result['count'] if result else 0

    @staticmethod
    def get_classes_by_teacher(teacher_id):
        """Get classes that have content created by a teacher. Fallback to all classes if none."""
        db = get_db()
        cur = db.cursor(dictionary=True)

        try:
            cur.execute(
                """
                SELECT DISTINCT c.*
                FROM classes c
                LEFT JOIN materials m ON c.id = m.class_id AND m.created_by = %s
                LEFT JOIN quizzes q ON c.id = q.class_id AND q.created_by = %s
                LEFT JOIN assignments a ON c.id = a.class_id AND a.created_by = %s
                WHERE m.id IS NOT NULL OR q.id IS NOT NULL OR a.id IS NOT NULL
                ORDER BY c.name
                """,
                (teacher_id, teacher_id, teacher_id)
            )
            classes = cur.fetchall()
        except Exception:
            # Jika tabel belum ada, jatuh ke daftar semua kelas
            classes = []

        # Fallback: if teacher belum punya konten atau tabel belum ada, tampilkan semua kelas.
        if not classes:
            cur.execute("SELECT * FROM classes ORDER BY name")
            classes = cur.fetchall()

        cur.close()
        return classes