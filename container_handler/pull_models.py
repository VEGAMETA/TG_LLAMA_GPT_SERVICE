import logging
import asyncio
from asyncio.subprocess import DEVNULL

from src.project_config import config, models
from container_handler.containers import ContainerHandler


class ModelPuller():
    def __init__(self, models=models) -> None:
        self.models = models
        self.name = '_puller'

    async def start(self) -> None:
        await self.suspend_puller()
        await self.create_puller()
        await self.pull_models()
        logging.info('Pulling completed' if await self.suspend_puller() else 'Could not delete puller')
        logging.info('Everything is set up and ready')

    async def create_puller(self) -> None:
        container = 'ollama/ollama:0.1.29'
        if config.get('GPU').casefold() == 'amd':
            container += '-rocm'
        _, error = await ContainerHandler.run(
            'docker',
            'run',
            '-d',
            '-p',
            '11435:11434',
            '-v',
            'tg_llama_gpt_service_llm-service:/root/.ollama',
            '--name',
            f'ollama{self.name}',
            container, 
            stdout=DEVNULL,
        )
        if error:
            logging.error(f'Could not create puller - {error}')
        else:
            logging.info('Pulling models...')

    async def pull_model(self, model) -> None:
        logging.info(f'Pulling {model}...')
        _, error = await ContainerHandler.run(
            'docker',
            'exec',
            f'ollama{self.name}',
            'ollama',
            'pull',
            models.get(model),
            stdout=DEVNULL,
        )
        if b'open //./pipe/docker_engine' in error:
            return logging.error("Please run docker desktop")
        if b'success' not in error:
            logging.error(f'Could not pull model {model}') 
            if b'file does not exist' in error:
                logging.error(f'file {models.get(model)} does not exist')
                return models.pop(model)
            logging.error(error.decode())
        else:
            logging.info(f'Pulled {model}')

    async def pull_models(self) -> None:
        await asyncio.gather(*[self.pull_model(model) for model in self.models])

    async def suspend_puller(self) -> None:
        return await ContainerHandler.delete_container(self.name)
