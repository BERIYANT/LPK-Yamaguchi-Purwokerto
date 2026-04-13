from app import app
from utils.database import get_db

with app.app_context():
    db = get_db()
    cur = db.cursor()
    cur.execute("SHOW COLUMNS FROM users;")
    columns = [row[0] for row in cur.fetchall()]
    print("Columns:", columns)
