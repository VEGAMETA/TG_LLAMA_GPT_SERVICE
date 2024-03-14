import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Boolean, Column, Integer, String, SMALLINT, ARRAY, update
from sqlalchemy.engine.row import Row

from loader import db
from ollama_bot.misc.gpt import Models
from ollama_bot.models.base import Base
from ollama_bot.models.language import Languages


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, unique=True)
    balance = Column(Integer, default=0)
    context = Column(ARRAY(Integer), default=[])
    model = Column(String, default=Models.LLAMA2_TEST.name)
    language = Column(String, default=Languages.EN.name)
    server_id = Column(SMALLINT, default=0)
    permission = Column(SMALLINT, default=0)
    processing = Column(Boolean, default=False)

    @staticmethod
    async def create_user(user_id: int) -> Row:
        """
        Checks if user exists and adds new user to the table by user id.
        """
        existing_user = await User.get_user_by_id(user_id)
        if existing_user:
            logging.warning("Username already exists")
            return existing_user
        user = await User._new_user(user_id)
        return user

    @classmethod
    @db.with_session_no_commit_method
    async def get_user_by_id(cls, session: AsyncSession, user_id: int) -> Row:
        """
        Returns user Row by user id.
        """
        table = cls.__table__
        query = table.select().where(table.c.user_id == user_id)
        result = await session.execute(query)
        user = result.first()
        return user

    @staticmethod
    @db.with_session
    async def _new_user(session: AsyncSession, user_id: int) -> None:
        """
        Adds new user by user id.
        """
        user = User(user_id=user_id)
        session.add(user)

    @classmethod
    @db.with_session_method
    async def set_language(cls, session: AsyncSession, user_id: int, language: Languages) -> None:
        """
        Sets user language for given user (by id).
        """
        table = cls.__table__
        stmt = table.update().where(table.c.user_id == user_id).values(language=language.name)
        await session.execute(stmt)

    @classmethod
    @db.with_session_method
    async def set_model(cls, session: AsyncSession, user_id: int, model: Models) -> None:
        """
        Sets model for user for given user (by id).
        """
        table = cls.__table__
        stmt = table.update().where(table.c.user_id == user_id).values(model=model.name)
        await session.execute(stmt)

    @classmethod
    @db.with_session_method
    async def set_context(cls, session: AsyncSession, user_id: int, context: list[int]) -> None:
        """
        Sets context for user for given user (by id).
        """
        table = cls.__table__
        stmt = table.update().where(table.c.user_id == user_id).values(context=context)
        await session.execute(stmt)

    @classmethod
    @db.with_session_method
    async def set_processing(cls, session: AsyncSession, user_id: int, flag: bool) -> None:
        """
        Sets user processing flag for given user (by id).
        """
        table = cls.__table__
        stmt = table.update().where(table.c.user_id == user_id).values(processing=flag)
        await session.execute(stmt)

    @staticmethod
    async def get_language(user_id) -> Languages:
        """
        Returns user language dictionary by user id.
        """
        user = await User.get_user_by_id(user_id)
        for language in Languages:
            if language.name == user.language:
                return language.value.dictionary
        else:
            logging.warning("Language not found")
            return Languages.EN.value.dictionary

    @staticmethod
    @db.with_session
    async def get_model(user_id) -> Models:
        """
        Returns chosen user model by user id.
        """
        user = await User.get_user_by_id(user_id)
        for model in Models:
            if model.name == user.model:
                return model.value
        else:
            logging.warning("Model not found")
            return Models.LLAMA2_TEST.name

    @staticmethod
    async def get_context(user_id) -> list[int]:
        """
        Returns user context by user id.
        """
        user = await User.get_user_by_id(user_id)
        return user.context

    @staticmethod
    async def get_processing(user_id) -> bool:
        """
        Returns user processing flag by user id.
        """
        user = await User.get_user_by_id(user_id)
        return user.processing
