from dataclasses import dataclass
from datetime import datetime

@dataclass 
class Expense:
    id : int
    amount : float
    category : str
    date : datetime
    description : str
