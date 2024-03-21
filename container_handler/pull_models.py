import asyncio
import logging
from asyncio.subprocess import DEVNULL
from src.project_config import config, models
from container_handler.commands import Commands
from container_handler.containers import ContainerHandler


class ModelPuller():
    def __init__(self, models=models) -> None:
        self.models = models
        self.name = '_puller'

    async def start(self) -> None:
        await self.suspend_puller()
        await self.create_puller()
        await asyncio.gather(*[self.pull_model(model) for model in self.models])
        logging.info('Pulling completed' if await self.suspend_puller() else 'Could not delete puller')
        logging.info('Everything is set up and ready')

    async def create_puller(self) -> None:
        container = "ollama/ollama:0.1.29"
        container += "-rocm" if config.get('GPU').casefold() == "amd" else ""
        _, error = await ContainerHandler.run(*Commands.run_puller(self.name), container, stdout=DEVNULL)
        if error and b'Pull complete' not in error:
            logging.error(f'Could not create puller - {error}')
        else:
            logging.info('Pulling models...')

    async def pull_model(self, model_name) -> None:
        model = models.get(model_name)
        logging.info(f'Pulling {model}...')
        _, error = await ContainerHandler.run(*Commands.pull(self.name), model, stdout=DEVNULL)
        if error and b'success' not in error:
            logging.error(f'Could not pull model {model}')
            if b'file does not exist' in error:
                logging.error(f'file {model} does not exist')
                return models.pop(model_name)
            logging.error(error.decode())
        else:
            logging.info(f'Pulled {model}')

    async def suspend_puller(self) -> None:
        return await ContainerHandler.delete_container(self.name)
