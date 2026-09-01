"""
Lightweight SQLite persistence layer. No ORM needed for a hackathon
project - plain sqlite3 keeps this dependency-free and easy to read.
"""

import os
import sqlite3


def get_connection(db_path: str) -> sqlite3.Connection:
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str) -> None:
    """Creates the analyses table if it doesn't already exist."""
    conn = get_connection(db_path)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            sentiment_label TEXT NOT NULL,
            sentiment_score REAL NOT NULL,
            emotion_label TEXT NOT NULL,
            emotion_score REAL NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def save_analysis(
    db_path: str,
    text: str,
    sentiment_label: str,
    sentiment_score: float,
    emotion_label: str,
    emotion_score: float,
    created_at: str,
) -> None:
    conn = get_connection(db_path)
    conn.execute(
        """
        INSERT INTO analyses
            (text, sentiment_label, sentiment_score, emotion_label, emotion_score, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (text, sentiment_label, sentiment_score, emotion_label, emotion_score, created_at),
    )
    conn.commit()
    conn.close()


def get_all_analyses(db_path: str, limit: int = 200) -> list:
    conn = get_connection(db_path)
    rows = conn.execute(
        "SELECT * FROM analyses ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_summary_stats(db_path: str) -> dict:
    """Aggregate counts used to power the pie/bar charts on the history page."""
    conn = get_connection(db_path)

    sentiment_rows = conn.execute(
        "SELECT sentiment_label, COUNT(*) as count FROM analyses GROUP BY sentiment_label"
    ).fetchall()

    emotion_rows = conn.execute(
        "SELECT emotion_label, COUNT(*) as count FROM analyses GROUP BY emotion_label"
    ).fetchall()

    total = conn.execute("SELECT COUNT(*) as count FROM analyses").fetchone()["count"]

    conn.close()

    return {
        "total": total,
        "sentiment_breakdown": [dict(row) for row in sentiment_rows],
        "emotion_breakdown": [dict(row) for row in emotion_rows],
    }
