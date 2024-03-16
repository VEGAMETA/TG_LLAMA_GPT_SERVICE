import logging
import asyncio
from asyncio.subprocess import DEVNULL
from container_handler.containers import ContainerHandler
from src.project_config import config


class ModelPuller():
    def __init__(self, models=config.get('Models').values()) -> None:
        self.models = models
        self.name = '_puller'

    async def start(self) -> None:
        await self.create_puller()
        await self.pull_models()
        await self.suspend_puller()

    async def create_puller(self) -> None:
        out, error = await ContainerHandler.run(
            'docker',
            'run',
            '-d',
            '-p',
            '11435:11434',
            '-v',
            'tg_llama_gpt_service_llm-service:/root/.ollama',
            '--name',
            f'ollama{self.name}',
            'ollama/ollama:0.1.27',  # 0.1.29
            stdout=DEVNULL,
        )
        if error:
            logging.error('Could not create puller')
        else:
            logging.info('Pulling models...')

    async def pull_model(self, model) -> None:
        _, error = await ContainerHandler.run(
            'docker',
            'exec',
            f'ollama{self.name}',
            'ollama',
            'pull',
            model,
            stdout=DEVNULL,
        )
        if error:
            logging.error(f'Could not pull model {model}')
        else:
            logging.info(f'Pulled {model}')

    async def pull_models(self) -> None:
        await asyncio.gather(*[self.pull_model(model) for model in self.models])

    async def suspend_puller(self) -> None:
        if await ContainerHandler.delete_container(self.name):
            logging.info('Pulling completed')
        else:
            logging.error('Could not delete puller')
