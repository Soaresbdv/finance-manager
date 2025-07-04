import sqlite3
from contextlib import contextmanager

@contextmanager
def get_db():
    conn = sqlite3.connect('finance.db')
    try:
        conn.execute('''CREATE TABLE IF NOT EXISTS users
                       (email TEXT PRIMARY KEY, password TEXT)''')
        yield conn
    finally:
        conn.close()