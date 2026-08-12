import sqlite3
from datetime import datetime
from pathlib import Path

from app.config import settings
from app.exceptions import DatabaseError
from app.models.expense import Expense
from app.repositories.interface import ExpenseRepositoryInterface


class SQLiteExpenseRepository(ExpenseRepositoryInterface):

    def __init__(self, database=None):
        self.database = database or settings.database_path
        self._create_table()

    def _connect(self):
        return sqlite3.connect(self.database)

    def _create_table(self):

        try:
            Path(self.database).parent.mkdir(
                parents=True,
                exist_ok=True
            )

            with self._connect() as connection:
                connection.execute("""
                    CREATE TABLE IF NOT EXISTS expenses (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        amount REAL NOT NULL,
                        category TEXT NOT NULL,
                        description TEXT NOT NULL,
                        date TEXT NOT NULL
                    )
                """)

        except sqlite3.Error as error:
            raise DatabaseError(
                f"Failed to initialize database: {error}"
            ) from error

    def add(self, expense: Expense) -> int:

        try:
            with self._connect() as connection:

                cursor = connection.execute(
                    """
                    INSERT INTO expenses
                    (amount, category, description, date)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        expense.amount,
                        expense.category,
                        expense.description,
                        expense.date.isoformat()
                    )
                )

                return cursor.lastrowid

        except sqlite3.Error as error:
            raise DatabaseError(
                f"Failed to add expense: {error}"
            ) from error

    def get_all(self) -> list[Expense]:

        try:
            with self._connect() as connection:

                rows = connection.execute(
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
                    date=datetime.fromisoformat(row[4])
                )
                for row in rows
            ]

        except sqlite3.Error as error:
            raise DatabaseError(
                f"Failed to retrieve expenses: {error}"
            ) from error

    def get_by_id(self, expense_id: int) -> Expense | None:

        try:
            with self._connect() as connection:

                row = connection.execute(
                    """
                    SELECT id, amount, category, description, date
                    FROM expenses
                    WHERE id = ?
                    """,
                    (expense_id,)
                ).fetchone()

            if row is None:
                return None

            return Expense(
                id=row[0],
                amount=row[1],
                category=row[2],
                description=row[3],
                date=datetime.fromisoformat(row[4])
            )

        except sqlite3.Error as error:
            raise DatabaseError(
                f"Failed to retrieve expense: {error}"
            ) from error

    def update(self, expense: Expense) -> bool:

        try:
            with self._connect() as connection:

                cursor = connection.execute(
                    """
                    UPDATE expenses
                    SET amount = ?,
                        category = ?,
                        description = ?
                    WHERE id = ?
                    """,
                    (
                        expense.amount,
                        expense.category,
                        expense.description,
                        expense.id
                    )
                )

                return cursor.rowcount > 0

        except sqlite3.Error as error:
            raise DatabaseError(
                f"Failed to update expense: {error}"
            ) from error

    def delete(self, expense_id: int) -> bool:

        try:
            with self._connect() as connection:

                cursor = connection.execute(
                    """
                    DELETE FROM expenses
                    WHERE id = ?
                    """,
                    (expense_id,)
                )

                return cursor.rowcount > 0

        except sqlite3.Error as error:
            raise DatabaseError(
                f"Failed to delete expense: {error}"
            ) from error
