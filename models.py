from dataclasses import dataclass

@dataclass
class Account:
    name: str
    mask: str
    balance: float

@dataclass
class BillItem:
    service: str
    cost: float
