from utils.database import get_db
from werkzeug.security import generate_password_hash, check_password_hash

class UserModel:
    @staticmethod
    def get_by_id(user_id):
        db = get_db()
        cur = db.cursor(dictionary=True, buffered=True)
        cur.execute("SELECT * FROM users WHERE id=%s", (user_id,))
        user = cur.fetchone()
        cur.close()
        return user

    @staticmethod
    def get_by_username(username):
        db = get_db()
        cur = db.cursor(dictionary=True, buffered=True)
        cur.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cur.fetchone()
        cur.close()
        return user

    @staticmethod
    def get_by_email(email):
        """Get user by email"""
        db = get_db()
        cur = db.cursor(dictionary=True, buffered=True)
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()
        return user

    @staticmethod
    def create_user(username, password, role='student', full_name='', bio='', email='', phone=''):
        db = get_db()
        cur = db.cursor(buffered=True)
        hashed_password = generate_password_hash(password)
        cur.execute(
            """INSERT INTO users (username, password, role, full_name, bio, email, phone) 
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (username, hashed_password, role, full_name, bio, email, phone)
        )
        db.commit()
        user_id = cur.lastrowid
        cur.close()
        return user_id

    @staticmethod
    def update_user(user_id, username, full_name, role, bio=None, avatar=None, email=None, phone=None):
        db = get_db()
        cur = db.cursor(buffered=True)
        if bio and avatar:
            cur.execute(
                """UPDATE users SET username=%s, full_name=%s, role=%s, bio=%s, 
                   avatar=%s, email=%s, phone=%s WHERE id=%s""",
                (username, full_name, role, bio, avatar, email, phone, user_id)
            )
        elif bio:
            cur.execute(
                """UPDATE users SET username=%s, full_name=%s, role=%s, bio=%s, 
                   email=%s, phone=%s WHERE id=%s""",
                (username, full_name, role, bio, email, phone, user_id)
            )
        elif avatar:
            cur.execute(
                """UPDATE users SET username=%s, full_name=%s, role=%s, avatar=%s, 
                   email=%s, phone=%s WHERE id=%s""",
                (username, full_name, role, avatar, email, phone, user_id)
            )
        else:
            cur.execute(
                """UPDATE users SET username=%s, full_name=%s, role=%s, 
                   email=%s, phone=%s WHERE id=%s""",
                (username, full_name, role, email, phone, user_id)
            )
        db.commit()
        cur.close()

    @staticmethod
    def update_password(user_id, new_password):
        db = get_db()
        cur = db.cursor(buffered=True)
        hashed_password = generate_password_hash(new_password)
        cur.execute("UPDATE users SET password=%s WHERE id=%s", (hashed_password, user_id))
        db.commit()
        cur.close()

    @staticmethod
    def delete_user(user_id):
        db = get_db()
        cur = db.cursor(buffered=True)
        cur.execute("DELETE FROM users WHERE id=%s", (user_id,))
        db.commit()
        cur.close()

    @staticmethod
    def get_all_users():
        db = get_db()
        cur = db.cursor(dictionary=True, buffered=True)
        cur.execute("SELECT * FROM users ORDER BY role, username")
        users = cur.fetchall()
        cur.close()
        return users