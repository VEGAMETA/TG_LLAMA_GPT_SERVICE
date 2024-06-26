import logging
from asyncio.subprocess import DEVNULL
from container_handler.commands import Commands
from container_handler.containers import ContainerHandler


class Composer():

    async def start(self):
        await self.create_network()
        await self.down()
        await self.build()
        await self.cleanup()
        await self.up()

    async def create_network(self):
        await ContainerHandler.run(*Commands.create_network, stdout=DEVNULL)
    
    async def cleanup(self):
        images, _ = await ContainerHandler.run(*Commands.get_dangling, stdout=DEVNULL)
        if images:
            images = images.decode().split('\n')
            logging.info(images)
            await ContainerHandler.run(*Commands.remove_images, *images)
        logging.info("Cleanup completed")

    async def build(self):
        logging.info("Building containers...")
        _, error = await ContainerHandler.run(*Commands.build, stdout=DEVNULL)
        if error and b'file has already been closed' not in error:
            logging.error(f"Could not build containers - {error.decode()}")
        else:
            logging.info("All Containers are built")

    async def up(self):
        logging.info("Starting containers...")
        _, error = await ContainerHandler.run(*Commands.up, stdout=DEVNULL)
        if (b'postgres  Started' in error or b'postgres  Running' in error) and b'python  Started' in error:
            logging.info("All Containers are started")
        else:
            logging.error(f"Could not start containers - {error.decode()}")

    async def down(self):
        logging.info("Stopping containers...")
        await ContainerHandler.run(*Commands.down, stdout=DEVNULL)
        logging.info("All Containers are stopped")
