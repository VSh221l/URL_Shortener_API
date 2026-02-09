import sqlite3
from contextlib import contextmanager
import os
from logging_config import logger

URLS_TABLE = "urls"

def get_db_path():
    path = os.getenv("DATABASE_PATH", "urls.db")
    logger.info(f"DB PATH: {path}")
    return path

def init_db() -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {URLS_TABLE} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE NOT NULL,
                original_url TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
    logger.info('Database initialized')


@contextmanager
def get_connection():
    conn = sqlite3.connect(get_db_path())
    try:
        yield conn
    except Exception as e:
        conn.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        conn.close()