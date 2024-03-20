import logging
from asyncio.subprocess import DEVNULL

from container_handler.containers import ContainerHandler


class Composer():

    async def start(self):
        await self.down()
        await self.build()
        await self.cleanup()
        await self.up()

    async def cleanup(self):
        images, _ = await ContainerHandler.run(
            'docker',
            'images',
            '-f',
            'dangling=true',
            '-q',
            stderr=DEVNULL,
        )
        images = images.decode().split('\n')
        await ContainerHandler.run(
            'docker',
            'rmi',
            '-f',
            *images,
        )
        logging.info("Cleanup completed")

    async def build(self):
        logging.info("Building containers...")
        _, error = await ContainerHandler.run(
            'docker-compose',
            'build',
            stdout=DEVNULL
        )
        if  error and b'file has already been closed' not in error:
            logging.error(f"Could not build containers - {error.decode()}")
        else:
            logging.info("All Containers are built")

    async def up(self):
        logging.info("Starting containers...")
        _, error = await ContainerHandler.run(
            'docker-compose',
            'up',
            '-d',
            stdout=DEVNULL
        )
        if (b'postgres  Started' in error
                or b'postgres  Running' in error)\
                and b'python  Started' in error:
            logging.info("All Containers are started")
        else:
            logging.error(f"Could not start containers - {error.decode()}")

    async def down(self):
        logging.info("Stopping containers...")
        await ContainerHandler.run(
            'docker-compose',
            'down',
            stdout=DEVNULL
        )
        logging.info("All Containers are stopped")
