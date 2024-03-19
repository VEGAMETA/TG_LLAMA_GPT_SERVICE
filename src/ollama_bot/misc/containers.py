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
            while True:
                query = select(Container).filter(Container.port == port)
                container = (await session.execute(query)).scalar()
                sleeptime = datetime.now() - container.last_activity_time + timedelta(minutes=30)
                sleeptime = sleeptime.total_seconds()
                while sleeptime > 0:
                    await asyncio.sleep(sleeptime)
                else:
                    if not container.operating:
                        await delete_container(port)
                        await session.delete(container)
                        await session.commit()
                        return
                    container.last_activity_time = datetime.now()
                    await session.commit()
                await session.refresh(container)


async def get_container_port(session: AsyncSession, model: str) -> int:
    """
    Returns container.
    """
    while True:
        query = select(Container).filter(Container.operating == False)
        container = (await session.execute(query)).scalar()
        if container:
            container.operating = True
            await session.commit()
            return container.port
        port = await get_free_port(session, model)
        if port:
            container = Container(port=port, operating=True)
            await session.merge(container)
            await session.commit()
            return port
        asyncio.sleep(5)
        session.expire_all()


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
    query = select(Container).filter(Container.port == port)
    container = (await session.execute(query)).scalar()
    container.operating = False

async def delete_container(port):
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
