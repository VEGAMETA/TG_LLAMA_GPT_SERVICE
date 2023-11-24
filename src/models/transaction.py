import enum
import datetime


class TransactionState(enum.Enum):
    ...


class Transaction:
    def __init__(self) -> None:
        self.id: 0 = 0
        self.user_id: int = 0
        self.transaction_time: datetime.datetime = ...
        self.transaction_state: TransactionState = ...
        self.transaction_expire_time: datetime.datetime = ...
