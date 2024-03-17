from datetime import datetime

from sqlalchemy.engine.row import Row
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import ForeignKey, Column, Integer, Boolean, DateTime, SMALLINT

from loader import db
from ollama_bot.models.base import Base


class Container(Base):
    __tablename__ = "containers"

    id = Column(Integer, primary_key=True)
    operating = Column(Boolean, default=False)
    last_activity_time = Column(DateTime, default=datetime.now())
    port = Column(Integer)
