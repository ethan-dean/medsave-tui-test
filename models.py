from dataclasses import dataclass

@dataclass
class Account:
    name: str
    mask: str
    balance: float

@dataclass
class Transaction:
    transaction_id: str
    account_id: int
    date: str
    amount: float
    merchant_name: str
    category: str
    running_balance: float
    pending: bool
    description: str

@dataclass
class BillItem:
    service: str
    cost: float

