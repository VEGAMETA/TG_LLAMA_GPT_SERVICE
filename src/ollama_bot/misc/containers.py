import asyncio
import aiohttp
import logging
from sqlalchemy.future import select
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from project_config import config
from ollama_bot.models.container import Container

server_port = config.get('CONTAINER_HANDLER_SERVER_PORT', 11433)
blocked_ports = set()


async def add_container(session: AsyncSession, port: int) -> None:
    """
    Add container.
    """
    await session.merge(Container(port=port, operating=False))


async def wait_for_suspend(port: int) -> None:
    """
    Wait for suspend.
    """
    from loader import sessionmaker
    async with sessionmaker() as session:
        async with session.begin():
            container = await session.get(Container, port)
            while True:
                sleeptime = 1
                while sleeptime > 0:
                    future_time = container.last_activity_time + timedelta(minutes=30)
                    sleeptime = (future_time - datetime.now()).total_seconds()
                    await asyncio.sleep(round(sleeptime) + 1)
                    await session.refresh(container)
                if not container.operating:
                    await delete_container(port)
                    await session.delete(container)
                    await session.commit()
                    return
                container.last_activity_time = datetime.now()
                await session.commit()

async def get_container_port(session: AsyncSession, model: str) -> int:
    """
    Returns container.
    """
    while True:
        session.expire_all()
        query = select(Container).filter(Container.operating == False)
        container = (await session.execute(query)).scalar()
        if container:
            container.operating = True
            container.last_activity_time = datetime.now()
            await session.commit()
            await check_container(container.port)
            return container.port
        port = await get_free_port(session, model)
        if port:
            container = Container(port=port, operating=True)
            await session.merge(container)
            await session.commit()
            await check_container(port)
            asyncio.create_task(wait_for_suspend(container.port))
            return port
        asyncio.sleep(3)


async def get_free_port(session: AsyncSession, model: str) -> int:
    """
    Returns free port.
    """
    while True:
        session.expire_all()
        ports = {container[0].port for container in (await session.execute(select(Container))).fetchall()}
        reserved_ports = ports.union(blocked_ports)
        free_port = None
        for port in range(11435, 65535):
            if port not in reserved_ports:
                free_port = port
                break
        else:
            return None
        if await create_container(free_port, model):
            return free_port
        blocked_ports.add(free_port)


async def create_container(port: int, model: str) -> bool:
    """
    Creates container.
    """
    from loader import config as loader_config
    params = {'port': port, 'model': model}
    url = f'http://{loader_config.db.host}:{server_port}/create_container'
    async with aiohttp.ClientSession() as client_session:
        async with client_session.get(url, params=params) as response:
            logging.info(response.status)
            if response.status == 201:
                logging.info(await response.text())
                return True
            logging.error(await response.text())
            return False


async def unoperate(session: AsyncSession, port: int):
    container = await session.get(Container, port)
    container.operating = False

async def check_container(port: int) -> bool:
    from loader import config as loader_config
    params = {'port': port}
    url = f'http://{loader_config.db.host}:{server_port}/check_container'
    async with aiohttp.ClientSession() as client_session:
        async with client_session.get(url, params=params) as response:
            return response.status == 200

async def delete_container(port: int) -> bool:
    """
    Deletes container.
    """
    from loader import config as loader_config
    params = {'port': port}
    url = f'http://{loader_config.db.host}:{server_port}/delete_container'
    async with aiohttp.ClientSession() as client_session:
        async with client_session.get(url, params=params) as response:
            if response.status == 204:
                logging.info(f"Container with port {port} deleted")
                return True
            logging.error(await response.text())
            return False
