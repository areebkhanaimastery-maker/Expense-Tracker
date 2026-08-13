from dataclasses import dataclass
from datetime import datetime


@dataclass
class Expense:
    id: int | None
    amount: float
    category: str
    description: str
    date: datetime
