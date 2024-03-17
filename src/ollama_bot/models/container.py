import datetime

from sqlalchemy.engine.row import Row
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import ForeignKey, Column, Integer, Boolean, DateTime, SMALLINT

from ollama_bot.models.base import Base

from loader import db


class ContainerState(Base):
    __tablename__ = "containers"

    id = Column(Integer, primary_key=True)
    state = Column(SMALLINT, default=0)
    operating = Column(Boolean, default=False)
    last_activity_time = Column(DateTime, default=datetime.now())
    port = Column(Integer)
