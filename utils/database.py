import mysql.connector
import os
from flask import g
from config import Config, load_private_environment

def get_db():
    if 'db' not in g:
        # Worker Passenger dapat mempertahankan modul Config lama. Muat ulang
        # file privat tepat sebelum membuka koneksi agar request production
        # tidak pernah kembali memakai fallback lokal root/root.
        load_private_environment()
        db_config = {
            'host': os.getenv('DB_HOST', Config.DB_CONFIG['host']),
            'user': os.getenv('DB_USER', Config.DB_CONFIG['user']),
            'password': os.getenv('DB_PASSWORD', Config.DB_CONFIG['password']),
            'database': os.getenv('DB_NAME', Config.DB_CONFIG['database']),
            'port': int(os.getenv('DB_PORT', str(Config.DB_CONFIG['port']))),
        }
        g.db = mysql.connector.connect(**db_config)
    return g.db

def close_db(error=None):
    db = g.pop('db', None)
    if db:
        db.close()