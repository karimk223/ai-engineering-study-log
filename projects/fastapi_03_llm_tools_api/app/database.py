import json
import sqlite3
from contextlib import closing
from pathlib import Path

DATABASE_PATH = Path(__file__).resolve().parent.parent / "chats.db"


def init_database():
    with closing(sqlite3.connect(DATABASE_PATH)) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY,
                user_message TEXT NOT NULL,
                assistant_reply TEXT NOT NULL,
                model TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tool_calls (
                id INTEGER PRIMARY KEY,
                conversation_id INTEGER NOT NULL,
                tool_call_id TEXT NOT NULL,
                tool_name TEXT NOT NULL,
                arguments_json TEXT NOT NULL,
                result_json TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id)
            )
            """
        )
        connection.commit()


def save_chat(
    user_message: str,
    assistant_reply: str,
    model: str,
    tool_record: dict | None = None,
) -> int:
    with closing(sqlite3.connect(DATABASE_PATH)) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        with connection:
            cursor = connection.execute(
                """
                INSERT INTO conversations (user_message, assistant_reply, model)
                VALUES (?, ?, ?)
                """,
                (user_message, assistant_reply, model),
            )
            chat_id = cursor.lastrowid

            if tool_record is not None:
                connection.execute(
                    """
                    INSERT INTO tool_calls (
                        conversation_id, tool_call_id, tool_name,
                        arguments_json, result_json
                    )
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        chat_id,
                        tool_record["tool_call_id"],
                        tool_record["tool_name"],
                        json.dumps(tool_record["arguments"]),
                        json.dumps(tool_record["result"]),
                    ),
                )

        return chat_id

def get_chat(chat_id: int) -> dict | None:
    with closing(sqlite3.connect(DATABASE_PATH)) as connection:
        connection.row_factory = sqlite3.Row

        chat = connection.execute(
            """
            SELECT id, user_message, assistant_reply, model, created_at
            FROM conversations
            WHERE id = ?
            """,
            (chat_id,),
        ).fetchone()

        if chat is None:
            return None

        tool_rows = connection.execute(
            """
            SELECT id, tool_call_id, tool_name, arguments_json, result_json, created_at
            FROM tool_calls
            WHERE conversation_id = ?
            ORDER BY id
            """,
            (chat_id,),
        ).fetchall()

        record = dict(chat)
        record["tool_calls"] = [
            {
                "id": row["id"],
                "tool_call_id": row["tool_call_id"],
                "tool_name": row["tool_name"],
                "arguments": json.loads(row["arguments_json"]),
                "result": json.loads(row["result_json"]),
                "created_at": row["created_at"],
            }
            for row in tool_rows
        ]
        return record