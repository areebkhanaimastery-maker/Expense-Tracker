from abc import ABC, abstractmethod

from app.models.expense import Expense


class ExpenseRepositoryInterface(ABC):

    @abstractmethod
    def add(self, expense: Expense) -> int:
        pass

    @abstractmethod
    def get_all(self) -> list[Expense]:
        pass

    @abstractmethod
    def get_by_id(self, expense_id: int) -> Expense | None:
        pass

    @abstractmethod
    def update(self, expense: Expense) -> bool:
        pass

    @abstractmethod
    def delete(self, expense_id: int) -> bool:
        pass
