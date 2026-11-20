"""Parameterized MySQL operations for conversations and messages."""
from uuid import uuid4

from app.database.connection import database_cursor


def create_conversation(assistant_id: str, title: str) -> dict:
    conversation_id = str(uuid4())
    with database_cursor(commit=True) as cursor:
        cursor.execute(
            "INSERT INTO conversations (id, assistant_id, title) VALUES (%s, %s, %s)",
            (conversation_id, assistant_id, title),
        )
        cursor.execute(
            """
            SELECT c.id, c.assistant_id, a.name AS assistant_name, c.title,
                   c.created_at, c.updated_at
            FROM conversations c
            JOIN assistants a ON a.id = c.assistant_id
            WHERE c.id = %s
            """,
            (conversation_id,),
        )
        return cursor.fetchone()


def get_conversation(conversation_id: str) -> dict | None:
    with database_cursor() as cursor:
        cursor.execute(
            """
            SELECT c.id, c.assistant_id, a.name AS assistant_name, c.title,
                   c.created_at, c.updated_at
            FROM conversations c
            JOIN assistants a ON a.id = c.assistant_id
            WHERE c.id = %s
            """,
            (conversation_id,),
        )
        return cursor.fetchone()


def add_message(conversation_id: str, role: str, content: str) -> dict:
    with database_cursor(commit=True) as cursor:
        cursor.execute(
            "INSERT INTO messages (conversation_id, role, content) VALUES (%s, %s, %s)",
            (conversation_id, role, content),
        )
        message_id = cursor.lastrowid
        cursor.execute(
            "UPDATE conversations SET updated_at = CURRENT_TIMESTAMP WHERE id = %s",
            (conversation_id,),
        )
        cursor.execute(
            "SELECT id, role, content, created_at FROM messages WHERE id = %s",
            (message_id,),
        )
        return cursor.fetchone()


def list_messages(conversation_id: str) -> list[dict]:
    with database_cursor() as cursor:
        cursor.execute(
            """
            SELECT id, role, content, created_at
            FROM messages
            WHERE conversation_id = %s
            ORDER BY id ASC
            """,
            (conversation_id,),
        )
        return cursor.fetchall()


def list_conversations(limit: int = 20) -> list[dict]:
    with database_cursor() as cursor:
        cursor.execute(
            """
            SELECT c.id, c.assistant_id, a.name AS assistant_name, c.title,
                   c.created_at, c.updated_at
            FROM conversations c
            JOIN assistants a ON a.id = c.assistant_id
            ORDER BY c.updated_at DESC
            LIMIT %s
            """,
            (limit,),
        )
        return cursor.fetchall()


def delete_conversation(conversation_id: str) -> bool:
    with database_cursor(commit=True) as cursor:
        cursor.execute("DELETE FROM conversations WHERE id = %s", (conversation_id,))
        return cursor.rowcount > 0
