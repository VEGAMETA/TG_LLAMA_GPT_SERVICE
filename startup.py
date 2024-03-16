import sys
import logging
import asyncio
from container_handler.server import Server
from container_handler.pull_models import ModelPuller
from container_handler.composer import Composer

async def main() -> None:
    server = Server()
    puller = ModelPuller()
    composer = Composer()
    
    await asyncio.gather(
        server.start(), 
        puller.start(), 
        composer.start()
    )

if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s [%(levelname)s] - %(message)s',
        level=logging.INFO,
        stream=sys.stdout
    )

    try:
        asyncio.run(main())
    except KeyboardInterrupt as _:
        logging.info("Server stopped by user")
