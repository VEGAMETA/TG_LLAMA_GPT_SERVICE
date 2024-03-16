import logging
import asyncio
from asyncio.subprocess import PIPE
from project_config import config


class ContainerHandler:
    @staticmethod
    async def run(*args) -> tuple[bytes, bytes]:
        process = await asyncio.create_subprocess_exec(*args, stdout=PIPE, stderr=PIPE)
        return await process.communicate()

    @classmethod
    async def create_container(cls, port: int) -> bool:
        if bool(config.get('CPU')) or not config.get('GPU'):
            return not (await cls.run(
                'docker',
                'run',
                '-d',
                '--name',
                f'ollama{port}',
                '-p',
                f'{port}:11434',
                '--network',
                'tg_llama_gpt_service_tg_bot_network',
                'ollama/ollama:0.1.29',
            ))[1]

        if config.get('GPU').casefold() == 'nvidia':
            return not (await cls.run(
                'docker',
                'run',
                '-d',
                '--gpus=all',
                '--name',
                f'ollama{port}',
                '-p',
                f'{port}:11434',
                '--network',
                'tg_llama_gpt_service_tg_bot_network',
                '-v',
                'tg_llama_gpt_service_llm-service:/root/.ollama',
                'ollama/ollama:0.1.27', # 0.1.29
            ))[1]
        elif config.get('GPU').casefold() == 'amd':
            return not (await cls.run(
                'docker',
                'run',
                '-d',
                '--device',
                '/dev/kfd',
                '--device',
                '/dev/dri',
                '--name',
                f'ollama{port}',
                '-p',
                f'{port}:11434',
                '--network',
                'tg_llama_gpt_service_tg_bot_network',
                '-v',
                'tg_llama_gpt_service_llm-service:/root/.ollama',
                'ollama/ollama:0.1.29:rocm',
            ))[1]

    @classmethod
    async def _load_model(cls, port: int, model: str) -> str:
        return await cls.run(
            'docker',
            'exec',
            f'ollama{port}',
            'ollama',
            'run',
            f'{model}'
        )

    @classmethod
    async def start_container(cls, port: int) -> bool:
        return not (await cls.run('docker', 'start', f'ollama{port}'))[1]

    @classmethod
    async def stop_container(cls, port: int) -> bool:
        return not (await cls.run('docker', 'stop', f'ollama{port}'))[1]

    @classmethod
    async def delete_container(cls, port: int) -> bool:
        return not (await cls.run('docker', 'rm', f'ollama{port}'))[1] if await cls.stop_container(port) else False

    @classmethod
    async def prepare_container(cls, port: int, model: str) -> bool:
        _, error = await cls._load_model(port, model)
        
        if "No such container" in error.decode():
            return False
        
        if "is not running" in error.decode():
            logging.info(f"Container ollama{port} is not running trying to start it")
            if not await cls.start_container(port):
                return False
            _, error = await cls._load_model(port, model)
            return error
        
        return True
