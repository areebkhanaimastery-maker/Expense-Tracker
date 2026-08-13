"""
Database Connection Management.

Provides context manager for SQLite database connections with
PRAGMA enforcement, busy timeout, and automatic commit/rollback.
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from app.config import settings
from app.exceptions.database import DatabaseError


@contextmanager
def get_db_connection(
    db_path: Path | str | None = None,
) -> Generator[sqlite3.Connection, None, None]:
    """
    Context manager that yields an active SQLite connection.

    Enforces foreign keys, WAL journal mode, and busy timeout.
    Automatically commits on success or rolls back on exception.
    """
    target_path = Path(db_path) if db_path else settings.database_path

    # Ensure parent directory exists
    target_path.parent.mkdir(parents=True, exist_ok=True)

    conn = None
    try:
        conn = sqlite3.connect(
            str(target_path),
            timeout=settings.database_timeout,
        )
        conn.row_factory = sqlite3.Row

        # Execute PRAGMAs for concurrency and integrity
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        cursor.execute("PRAGMA journal_mode = WAL;")
        cursor.execute("PRAGMA busy_timeout = 10000;")
        cursor.close()

        yield conn

        conn.commit()

    except sqlite3.Error as error:
        if conn:
            try:
                conn.rollback()
            except sqlite3.Error:
                pass
        raise DatabaseError(f"Database error: {error}") from error

    finally:
        if conn:
            try:
                conn.close()
            except sqlite3.Error:
                pass
