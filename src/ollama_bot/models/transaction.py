import uuid
import enum
from datetime import datetime, timedelta

from sqlalchemy.engine.row import Row
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import ForeignKey, Column, Integer, DateTime, SMALLINT

from loader import db
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
    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    time = Column(DateTime, default=datetime.now())
    state = Column(SMALLINT, default=TransactionState.PENDING.value)
    expire_time = Column(
        DateTime, default=datetime.now() + timedelta(minutes=30))

    @staticmethod
    @db.with_session
    async def create_transaction(session: AsyncSession, user_id: int) -> UUID:
        transaction = Transaction(user_id=user_id)
        session.add(transaction)
        return transaction.uuid

    @classmethod
    @db.with_session_no_commit_method
    async def get_transactions_by_user_id(cls, session: AsyncSession, user_id: int) -> list['Transaction']:
        table = cls.__table__
        query = table.select().where(table.c.user_id == user_id)
        result = await session.execute(query)
        transactions = [row for row in result]
        return transactions

    @classmethod
    @db.with_session_no_commit_method
    async def get_transaction_by_uuid(cls, session: AsyncSession, uuid: UUID) -> Row:
        table = cls.__table__
        query = table.__table__.select().where(table.c.uuid == uuid)
        result = await session.execute(query)
        transaction = result.first()
        return transaction
