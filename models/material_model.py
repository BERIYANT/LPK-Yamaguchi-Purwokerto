from utils.database import get_db
from datetime import datetime

class MaterialModel:
    @staticmethod
    def create(title, content, class_id, created_by, file_path=None):
        db = get_db()
        cur = db.cursor()
        cur.execute(
            "INSERT INTO materials (title, content, file_path, class_id, created_by, created_at) VALUES (%s, %s, %s, %s, %s, %s)",
            (title, content, file_path, class_id, created_by, datetime.now())
        )
        db.commit()
        material_id = cur.lastrowid
        cur.close()
        return material_id

    @staticmethod
    def get_by_id(material_id):
        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT * FROM materials WHERE id=%s", (material_id,))
        material = cur.fetchone()
        cur.close()
        return material

    @staticmethod
    def get_by_class(class_id):
        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT * FROM materials WHERE class_id=%s ORDER BY created_at DESC", (class_id,))
        materials = cur.fetchall()
        cur.close()
        return materials

    @staticmethod
    def update(material_id, title, content, file_path=None):
        db = get_db()
        cur = db.cursor()
        if file_path is not None:
            cur.execute(
                "UPDATE materials SET title=%s, content=%s, file_path=%s WHERE id=%s",
                (title, content, file_path, material_id)
            )
        else:
            cur.execute(
                "UPDATE materials SET title=%s, content=%s WHERE id=%s",
                (title, content, material_id)
            )
        db.commit()
        cur.close()

    @staticmethod
    def delete(material_id):
        db = get_db()
        cur = db.cursor()
        cur.execute("DELETE FROM materials WHERE id=%s", (material_id,))
        db.commit()
        cur.close()