import sqlite3
from config import DATABASE

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS files (
                            id TEXT PRIMARY KEY,
                            filename TEXT,
                            filepath TEXT,
                            expiration TIMESTAMP,
                            download_limit INTEGER)''')
        conn.commit()