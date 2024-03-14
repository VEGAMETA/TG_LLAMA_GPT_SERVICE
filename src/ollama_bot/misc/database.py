from functools import wraps
from sqlalchemy.schema import CreateTable
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from ollama_bot.models.base import Base


class Database:
    def __init__(self, db_url):
        self.engine: AsyncEngine = create_async_engine(db_url)

    def get_session(self):
        return AsyncSession(self.engine)

    def get_connection(self):
        return self.engine.connect()

    async def migrate(self):
        async with self.get_connection() as conn:
            for table in Base.metadata.tables.values():
                await conn.execute(CreateTable(table, if_not_exists=True))

    def with_session(self, func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            async with self.get_session() as session:
                async with session.begin():
                    result = await func(session, *args, **kwargs)
                    await session.flush()
                    await session.commit()
            return result
        return wrapper

    def with_session_method(self, func):
        @wraps(func)
        async def wrapper(_self, *args, **kwargs):
            async with self.get_session() as session:
                async with session.begin():
                    result = await func(_self, session, *args, **kwargs)
                    await session.flush()
                    await session.commit()
            return result
        return wrapper

    def with_session_no_commit_method(self, func):
        @wraps(func)
        async def wrapper(_self, *args, **kwargs):
            async with self.get_session() as session:
                result = await func(_self, session, *args, **kwargs)
            return result
        return wrapper