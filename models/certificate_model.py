from utils.database import get_db
from datetime import datetime

class CertificateModel:
    @staticmethod
    def create(student_id, certificate_number, description=None, file_path=None, class_id=None):
        db = get_db()
        cur = db.cursor()
        cur.execute(
            """INSERT INTO certificates (student_id, class_id, certificate_number, description, file_path, issued_at) 
            VALUES (%s, %s, %s, %s, %s, %s)""",
            (student_id, class_id, certificate_number, description, file_path, datetime.now())
        )
        db.commit()
        certificate_id = cur.lastrowid
        cur.close()
        return certificate_id

    @staticmethod
    def get_by_id(certificate_id):
        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute(
            """SELECT c.*, u.username, u.full_name, cl.name as class_name
            FROM certificates c
            JOIN users u ON c.student_id = u.id
            LEFT JOIN classes cl ON c.class_id = cl.id
            WHERE c.id=%s""",
            (certificate_id,)
        )
        certificate = cur.fetchone()
        cur.close()
        return certificate

    @staticmethod
    def get_all():
        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute(
            """SELECT c.*, u.username, u.full_name, cl.name as class_name
            FROM certificates c
            JOIN users u ON c.student_id = u.id
            LEFT JOIN classes cl ON c.class_id = cl.id
            ORDER BY c.issued_at DESC"""
        )
        certificates = cur.fetchall()
        cur.close()
        return certificates

    @staticmethod
    def get_by_student(student_id):
        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute(
            """SELECT c.*, cl.name as class_name
            FROM certificates c
            LEFT JOIN classes cl ON c.class_id = cl.id
            WHERE c.student_id = %s
            ORDER BY c.issued_at DESC""",
            (student_id,)
        )
        certificates = cur.fetchall()
        cur.close()
        return certificates

    @staticmethod
    def update(certificate_id, student_id, certificate_number, description=None, file_path=None, class_id=None):
        db = get_db()
        cur = db.cursor()
        cur.execute(
            """UPDATE certificates 
            SET student_id=%s, class_id=%s, certificate_number=%s, description=%s, file_path=%s 
            WHERE id=%s""",
            (student_id, class_id, certificate_number, description, file_path, certificate_id)
        )
        db.commit()
        cur.close()

    @staticmethod
    def delete(certificate_id):
        db = get_db()
        cur = db.cursor()
        cur.execute("DELETE FROM certificates WHERE id=%s", (certificate_id,))
        db.commit()
        cur.close()