import sys
import logging
import asyncio
from container_handler.server import Server


async def main() -> None:
    server = Server()
    # run docker-compose build and up in the background
    # await asyncio.create_subprocess_shell('docker-compose', 'build')
    # await asyncio.create_subprocess_shell('docker-compose', 'up')
    await server.start()

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
