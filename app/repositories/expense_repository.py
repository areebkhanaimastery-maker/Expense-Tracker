"""
SQLite Expense Repository Implementation.
"""

from datetime import datetime
from pathlib import Path

from app.config import settings
from app.database import get_db_connection, init_db
from app.exceptions.database import DatabaseError, RepositoryError
from app.models.expense import Expense
from app.repositories.base import ExpenseRepositoryInterface


class SQLiteExpenseRepository(ExpenseRepositoryInterface):
    """SQLite implementation of ExpenseRepositoryInterface."""

    def __init__(self, database: str | Path | None = None):
        self.database = Path(database) if database else settings.database_path
        self._init_db()

    def _init_db(self):
        """Initialize database schema and indexes."""
        try:
            init_db(self.database)
        except Exception as error:
            raise RepositoryError(
                f"Failed to initialize database schema: {error}"
            ) from error

    def add(self, expense: Expense) -> int:
        """Add a new expense record."""
        try:
            with get_db_connection(self.database) as conn:
                cursor = conn.execute(
                    """
                    INSERT INTO expenses (amount, category, description, date)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        expense.amount,
                        expense.category,
                        expense.description,
                        expense.date.isoformat(),
                    ),
                )
                return cursor.lastrowid
        except Exception as error:
            raise RepositoryError(
                f"Failed to add expense: {error}"
            ) from error

    def get_all(self) -> list[Expense]:
        """Retrieve all expense records ordered by date DESC."""
        try:
            with get_db_connection(self.database) as conn:
                rows = conn.execute(
                    """
                    SELECT id, amount, category, description, date
                    FROM expenses
                    ORDER BY date DESC
                    """
                ).fetchall()

            return [
                Expense(
                    id=row[0],
                    amount=row[1],
                    category=row[2],
                    description=row[3],
                    date=datetime.fromisoformat(row[4]),
                )
                for row in rows
            ]
        except Exception as error:
            raise RepositoryError(
                f"Failed to retrieve expenses: {error}"
            ) from error

    def get_by_id(self, expense_id: int) -> Expense | None:
        """Retrieve an expense record by ID."""
        try:
            with get_db_connection(self.database) as conn:
                row = conn.execute(
                    """
                    SELECT id, amount, category, description, date
                    FROM expenses
                    WHERE id = ?
                    """,
                    (expense_id,),
                ).fetchone()

            if row is None:
                return None

            return Expense(
                id=row[0],
                amount=row[1],
                category=row[2],
                description=row[3],
                date=datetime.fromisoformat(row[4]),
            )
        except Exception as error:
            raise RepositoryError(
                f"Failed to retrieve expense #{expense_id}: {error}"
            ) from error

    def update(self, expense: Expense) -> bool:
        """Update an existing expense record."""
        try:
            with get_db_connection(self.database) as conn:
                cursor = conn.execute(
                    """
                    UPDATE expenses
                    SET amount = ?, category = ?, description = ?
                    WHERE id = ?
                    """,
                    (
                        expense.amount,
                        expense.category,
                        expense.description,
                        expense.id,
                    ),
                )
                return cursor.rowcount > 0
        except Exception as error:
            raise RepositoryError(
                f"Failed to update expense #{expense.id}: {error}"
            ) from error

    def delete(self, expense_id: int) -> bool:
        """Delete an expense record by ID."""
        try:
            with get_db_connection(self.database) as conn:
                cursor = conn.execute(
                    """
                    DELETE FROM expenses WHERE id = ?
                    """,
                    (expense_id,),
                )
                return cursor.rowcount > 0
        except Exception as error:
            raise RepositoryError(
                f"Failed to delete expense #{expense_id}: {error}"
            ) from error
