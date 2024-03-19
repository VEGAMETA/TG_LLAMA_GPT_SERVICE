import sys
import aiohttp
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.utils.token import TokenValidationError
from aiogram.utils.callback_answer import CallbackAnswerMiddleware
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, update, select

import project_config
from ollama_bot.models.base import Base
from ollama_bot.models.container import Container
from ollama_bot.config import load_config
from ollama_bot.middlwares.database import DbSessionMiddleware
from ollama_bot.handlers import default, language, models, subscription, gpt

logging.basicConfig(
    format='%(asctime)s [%(levelname)s] - %(message)s',
    level=logging.INFO,
    stream=sys.stdout
)

config = load_config()

config.db.base_url = f"{config.db.user}:{config.db.password}@{config.db.host}:{config.db.port}/{config.db.database}"
config.db.url = f"postgresql+asyncpg://{config.db.base_url}"

try:
    bot = Bot(token=config.tg_bot.token, parse_mode=ParseMode.HTML)
except TokenValidationError:
    logging.error("Invalid token")

engine = create_async_engine(url=config.db.url, echo=True)
sessionmaker = async_sessionmaker(engine, expire_on_commit=False)

dp = Dispatcher()
dp.update.middleware(DbSessionMiddleware(session_pool=sessionmaker))
dp.callback_query.middleware(CallbackAnswerMiddleware())

dp.include_router(default.router)
dp.include_router(language.router)
dp.include_router(models.router)
dp.include_router(subscription.router)
dp.include_router(gpt.router)


async def init_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.commit()
    async with sessionmaker() as session:
        async with session.begin():
            await fix_users_processing(session)
            await session.execute(delete(Container))
            await create_containers(session)
            await session.commit()
            await session.flush()

async def fix_users_processing(session: AsyncSession) -> None:
    from ollama_bot.models.user import User
    users = (await session.execute(select(User).filter(User.processing == True))).fetchall()
    for user in users:
        user[0].processing = False

async def create_containers(session: AsyncSession) -> None:
    ports = []
    port = project_config.config.get("CONTAINER_HANDLER_SERVER_PORT", 11433)
    async with aiohttp.ClientSession() as client_session:
        async with client_session.get(f"http://{config.db.host}:{port}/get_containers") as response:
            if response.status == 200:
                ports = (await response.text()).strip().split('\n')
        async with client_session.get(f"http://{config.db.host}:{port}/start_containers") as response:
            if response.status == 200:
                logging.info(f"Containers started")
    if ports:
        for port in ports:
            from ollama_bot.misc.containers import add_container, wait_for_suspend
            await add_container(session, int(port))
            asyncio.create_task(wait_for_suspend(int(port)))
        logging.info(f"Containers added to database")
