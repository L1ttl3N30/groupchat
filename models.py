import os
import sqlite3
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "chat.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create messages table if it does not exist."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                username TEXT,
                text TEXT NOT NULL
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def add_message(username: str, text: str):
    """Insert a new message into the database."""
    if not text:
        return

    username = username or "Anonymous"
    timestamp = datetime.utcnow().isoformat() + "Z"

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO messages (timestamp, username, text) VALUES (?, ?, ?)",
            (timestamp, username, text),
        )
        conn.commit()
    finally:
        conn.close()


def get_messages(limit: int | None = None):
    """Return all messages (or up to limit) as list of dicts."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        if limit is not None:
            cur.execute(
                "SELECT id, timestamp, username, text FROM messages ORDER BY id ASC LIMIT ?",
                (limit,),
            )
        else:
            cur.execute(
                "SELECT id, timestamp, username, text FROM messages ORDER BY id ASC"
            )
        rows = cur.fetchall()
        messages = []
        for row in rows:
            messages.append(
                {
                    "id": row["id"],
                    "timestamp": row["timestamp"],
                    "username": row["username"] or "Anonymous",
                    "text": row["text"],
                }
            )
        return messages
    finally:
        conn.close()


def clear_messages():
    """Delete all messages. Only used if admin mode is enabled."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM messages")
        conn.commit()
    finally:
        conn.close()
