import sys
import logging
import asyncio
import subprocess

from container_handler.server import Server
from container_handler.pull_models import ModelPuller
from container_handler.composer import Composer


def is_docker_running():
    result = subprocess.run(['docker', 'info'], capture_output=True, text=True)
    return 'ERROR' not in result.stderr


async def main() -> None:
    server = Server()
    puller = ModelPuller()
    composer = Composer()

    await composer.start()
    await asyncio.gather(
        server._start(),
        puller.start(),
    )

if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s [%(levelname)s] - %(message)s',
        level=logging.INFO,
        stream=sys.stdout
    )

    if not is_docker_running():
        logging.error("Could not start Docker")
        sys.exit(1)

    try:
        asyncio.run(main())
    except KeyboardInterrupt as _:
        logging.info("Server stopped by user")
