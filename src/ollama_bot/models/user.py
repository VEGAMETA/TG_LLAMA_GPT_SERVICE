from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import (
    Column,
    ForeignKey,
    Boolean,
    Integer,
    SmallInteger,
    BigInteger,
    String,
    UUID
)

from project_config import models
from ollama_bot.models.base import Base
from ollama_bot.misc.language import Languages


class User(Base):
    __tablename__ = "users"

    user_id = Column(BigInteger, primary_key=True,unique=True, autoincrement=False)
    balance = Column(Integer, default=0)
    context = Column(ARRAY(Integer), default=[])
    model = Column(String, default=next(iter(models)))
    language = Column(String, default=Languages.EN.name)
    permission = Column(SmallInteger, default=0)
    processing = Column(Boolean, default=False)
    transactions_ids = Column(ARRAY(Integer), default=[])
    container_id = Column(UUID(as_uuid=True), ForeignKey("containers.id"), default=None)
