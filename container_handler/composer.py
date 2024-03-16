import logging
import asyncio
from container_handler.containers import ContainerHandler


class Composer():

    async def start(self):
        await self.build()
        await self.up()

    async def build(self):
        _, error = await ContainerHandler.run(
            'docker-compose',
            'build',
            stdout=asyncio.subprocess.DEVNULL
        )
        if error:
            logging.error("Could not build containers")
        else:
            logging.info("All Containers are built")

    async def up(self):
        _, error = await ContainerHandler.run(
            'docker-compose',
            'up',
            '-d',
            stdout=asyncio.subprocess.DEVNULL
        )
        if error:
            logging.error("Could not start containers")
        else:
            logging.info("All Containers are started")
