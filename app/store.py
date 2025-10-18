import sqlite3
from datetime import datetime
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "call_logs.db")


def init_db():
    """Initialize the database (if not exists)."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS call_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            call_sid TEXT,
            from_number TEXT,
            to_number TEXT,
            user_message TEXT,
            ai_reply TEXT,
            created_at TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def log_interaction(call_sid: str, from_number: str, to_number: str, user_message: str, ai_reply: str):
    """Insert a single interaction (user message + AI reply) into the database."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO call_logs (call_sid, from_number, to_number, user_message, ai_reply, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (call_sid, from_number, to_number, user_message, ai_reply, datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()


def fetch_all():
    """Fetch all stored call logs."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT * FROM call_logs ORDER BY created_at DESC")
    rows = cur.fetchall()
    conn.close()
    return rows
