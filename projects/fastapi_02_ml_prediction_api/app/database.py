import sqlite3
from contextlib import closing
from pathlib import Path


DATABASE_PATH = Path(__file__).resolve().parent.parent / "predictions.db"


def init_database():
    with closing(sqlite3.connect(DATABASE_PATH)) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY,
                message TEXT NOT NULL,
                category TEXT NOT NULL,
                score REAL NOT NULL,
                model_version TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.commit()


def save_prediction(message: str, category: str, score: float, model_version: str):
    with closing(sqlite3.connect(DATABASE_PATH)) as connection:
        cursor = connection.execute(
            """
            INSERT INTO predictions (message, category, score, model_version)
            VALUES (?, ?, ?, ?)
            """,
            (message, category, score, model_version),
        )
        connection.commit()
        return cursor.lastrowid

def get_prediction(prediction_id: int):
    with closing(sqlite3.connect(DATABASE_PATH)) as connection:
        connection.row_factory = sqlite3.Row
        row = connection.execute(
            """
            SELECT id, message, category, score, model_version, created_at
            FROM predictions
            WHERE id = ?
            """,
            (prediction_id,),
        ).fetchone()
        return dict(row) if row is not None else None