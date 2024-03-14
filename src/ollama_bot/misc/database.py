from functools import wraps
from sqlalchemy.schema import CreateTable
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from ollama_bot.models.base import Base


class Database:
    """
    Database class.
    """

    def __init__(self, db_url):
        self.engine: AsyncEngine = create_async_engine(db_url)

    def get_session(self):
        """
        Returns AsyncSession.
        """
        return AsyncSession(self.engine)

    def get_connection(self):
        """
        Returns AsyncConnection.
        """
        return self.engine.connect()

    async def migrate(self):
        """
        Migrates database.
        """
        async with self.get_connection() as conn:
            for table in Base.metadata.tables.values():
                await conn.execute(CreateTable(table, if_not_exists=True))

    def with_session(self, func):
        """
        Decorator for async session with flush and commit.
        """
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
        """
        Method decorator for async session with flush and commit.
        """
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
        """
        Method decorator for async session without commit.
        """
        @wraps(func)
        async def wrapper(_self, *args, **kwargs):
            async with self.get_session() as session:
                result = await func(_self, session, *args, **kwargs)
            return result
        return wrapper
