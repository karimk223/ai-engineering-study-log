import sqlite3
from contextlib import closing
from pathlib import Path


DATABASE_PATH = Path(__file__).resolve().parent.parent / "customer_requests.db"


def init_database():
    with closing(sqlite3.connect(DATABASE_PATH)) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS customer_requests (
                id INTEGER PRIMARY KEY,
                customer_name TEXT NOT NULL,
                message TEXT NOT NULL
            )
            """
        )
        connection.commit()

def save_request(customer_name: str, message: str):
    with closing(sqlite3.connect(DATABASE_PATH)) as connection:
        cursor = connection.execute(
            "INSERT INTO customer_requests (customer_name, message) VALUES (?, ?)",
            (customer_name, message),
        )
        connection.commit()
        return cursor.lastrowid


def get_request(request_id: int):
    with closing(sqlite3.connect(DATABASE_PATH)) as connection:
        connection.row_factory = sqlite3.Row
        row = connection.execute(
            "SELECT id, customer_name, message FROM customer_requests WHERE id = ?",
            (request_id,),
        ).fetchone()
        return dict(row) if row is not None else None

def update_request(request_id: int, customer_name: str, message: str):
    with closing(sqlite3.connect(DATABASE_PATH)) as connection:
        connection.row_factory = sqlite3.Row
        row = connection.execute(
            """
            UPDATE customer_requests
            SET customer_name = ?, message = ?
            WHERE id = ?
            RETURNING id, customer_name, message
            """,
            (customer_name, message, request_id),
        ).fetchone()
        connection.commit()
        return dict(row) if row is not None else None

def delete_request(request_id: int):
    with closing(sqlite3.connect(DATABASE_PATH)) as connection:
        cursor = connection.execute(
            "DELETE FROM customer_requests WHERE id = ?",
            (request_id,),
        )
        connection.commit()
        return cursor.rowcount > 0

def list_requests(limit: int, offset: int):
    with closing(sqlite3.connect(DATABASE_PATH)) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            """
            SELECT id, customer_name, message
            FROM customer_requests
            ORDER BY id
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
        ).fetchall()
        return [dict(row) for row in rows]
