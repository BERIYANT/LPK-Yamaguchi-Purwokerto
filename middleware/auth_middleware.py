from flask import session, g
from utils.database import get_db

def load_user():
    user_id = session.get("user_id")
    if user_id:
        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT * FROM users WHERE id=%s", (user_id,))
        g.user = cur.fetchone()
        cur.close()
    else:
        g.user = None