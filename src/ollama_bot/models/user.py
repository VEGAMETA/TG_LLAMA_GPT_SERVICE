from __future__ import annotations

from typing import Set
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy import Column, Boolean, Integer, BigInteger, String, DateTime

from project_config import models
from ollama_bot.models.base import Base
from ollama_bot.misc.language import Languages


class User(Base):
    __tablename__ = "users"

    user_id = Column(BigInteger, primary_key=True,unique=True, autoincrement=False, index=True)
    balance = Column(Integer, default=0)
    context = Column(ARRAY(Integer), default=[])
    model = Column(String, default=next(iter(models)))
    language = Column(String, default=Languages.EN.name)
    subscription = Column(Boolean, default=False)
    subscription_expire_time = Column(DateTime, default=None, nullable=True)
    processing = Column(Boolean, default=False)
    transactions: Mapped[Set["Transaction"]] = relationship(back_populates="user")
