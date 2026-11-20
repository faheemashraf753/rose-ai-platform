"""MySQL connection helpers. Database credentials come only from the environment."""
from contextlib import contextmanager
from typing import Any, Iterator

import mysql.connector

from app.config import settings


class DatabaseUnavailableError(RuntimeError):
    """Raised when MySQL cannot serve an application request."""


def get_connection():
    try:
        return mysql.connector.connect(
            host=settings.database_host,
            port=settings.database_port,
            database=settings.database_name,
            user=settings.database_user,
            password=settings.database_password,
            connection_timeout=5,
            autocommit=False,
        )
    except mysql.connector.Error as exc:
        raise DatabaseUnavailableError(
            "MySQL is unavailable. Start MySQL and check the DATABASE_* settings in .env."
        ) from exc


@contextmanager
def database_cursor(commit: bool = False) -> Iterator[Any]:
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        yield cursor
        if commit:
            connection.commit()
    except mysql.connector.Error as exc:
        connection.rollback()
        raise DatabaseUnavailableError(
            "MySQL could not complete that request. Check the database setup and try again."
        ) from exc
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


def check_database_connection() -> bool:
    try:
        with database_cursor() as cursor:
            cursor.execute("SELECT 1 AS ready")
            return cursor.fetchone()["ready"] == 1
    except DatabaseUnavailableError:
        return False
