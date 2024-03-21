from sqlalchemy import func, Column, Boolean, Integer, DateTime, UUID

from ollama_bot.models.base import Base


class Container(Base):
    __tablename__ = "containers"

    id = Column(UUID(as_uuid=True), server_default=func.gen_random_uuid())
    operating = Column(Boolean, default=False)
    last_activity_time = Column(DateTime, server_default=func.now())
    port = Column(Integer, primary_key=True)
