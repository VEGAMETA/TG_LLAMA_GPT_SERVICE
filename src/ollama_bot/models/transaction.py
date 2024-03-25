from __future__ import annotations

import enum
from datetime import datetime, timedelta
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy import func, Column, Integer, SmallInteger, DateTime, UUID, ForeignKey

from ollama_bot.models.base import Base


class TransactionState(enum.Enum):
    PENDING = 0
    COMPLETED = 1
    PROCESSING = 2
    PAID = 3
    CONFIRMING = 4
    EXPIRED = 5
    DENIED = 6
    FAILED = 7
    CANCELING = 8
    CANCELED = 9


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, autoincrement=True)
    uuid = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    user_id = Column(Integer, ForeignKey('users.user_id'), index=True)
    user: Mapped["User"] = relationship(back_populates="transactions")
    time= Column(DateTime, server_default=func.now())
    state = Column(SmallInteger, default=TransactionState.PENDING.value)
    expire_time = Column(DateTime, default=datetime.now() + timedelta(minutes=30))
