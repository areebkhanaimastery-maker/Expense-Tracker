"""
Database Schema Initialization and Management.

Defines table schemas, indexes, and schema verification.
"""

from pathlib import Path

from app.database.connection import get_db_connection
from app.exceptions.database import DatabaseError


CREATE_EXPENSES_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount REAL NOT NULL CHECK (amount > 0),
    category TEXT NOT NULL,
    description TEXT NOT NULL,
    date TEXT NOT NULL
);
"""

CREATE_INDEX_DATE_SQL = """
CREATE INDEX IF NOT EXISTS idx_expenses_date ON expenses(date);
"""

CREATE_INDEX_CATEGORY_SQL = """
CREATE INDEX IF NOT EXISTS idx_expenses_category ON expenses(category);
"""


def init_db(db_path: Path | str | None = None) -> None:
    """
    Initialize the database schema and indexes.
    """
    try:
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(CREATE_EXPENSES_TABLE_SQL)
            cursor.execute(CREATE_INDEX_DATE_SQL)
            cursor.execute(CREATE_INDEX_CATEGORY_SQL)
            cursor.close()
    except Exception as e:
        raise DatabaseError(f"Failed to initialize database schema: {e}") from e


def verify_schema(db_path: Path | str | None = None) -> bool:
    """
    Verify that required database tables and columns exist.
    """
    try:
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(expenses);")
            columns = {row[1] for row in cursor.fetchall()}
            cursor.close()

            required = {"id", "amount", "category", "description", "date"}
            return required.issubset(columns)
    except Exception:
        return False
