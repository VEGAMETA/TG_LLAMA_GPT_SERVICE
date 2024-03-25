import logging
import asyncio
import aiohttp
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

import project_config
from loader import config
from ollama_bot.models.base import Base
from ollama_bot.models.user import User
from ollama_bot.models.container import Container

async def init_tables(engine, sessionmaker) -> None:
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
    users = (await session.execute(select(User).filter(User.processing == True))).fetchall()
    for user in users:
        user[0].processing = False

async def create_containers(session: AsyncSession) -> None:
    ports = []
    port = project_config.config.get("CONTAINER_HANDLER_SERVER_PORT", 11433)
    async with aiohttp.ClientSession() as client_session:
        async with client_session.get(f"http://{config.db.host}:{port}/get_containers") as response:
            if response.status == 200:
                ports.extend((await response.text()).strip().split('\n'))
        async with client_session.get(f"http://{config.db.host}:{port}/start_containers") as response:
            if response.status == 200:
                logging.info(f"Containers started")
    if ports:
        for port in ports:
            from ollama_bot.misc.containers import add_container, wait_for_suspend
            await add_container(session, int(port))
            asyncio.create_task(wait_for_suspend(int(port)))
        logging.info(f"Containers added to database")

async def indexing(session: AsyncSession) -> None:
    await session.execute(delete(User))
    await session.execute(delete(Container))
    await session.commit()