import asyncio
import logging
from asyncio.subprocess import PIPE
from src.project_config import config
from container_handler.commands import Commands


class ContainerHandler:
    @staticmethod
    async def run(*args, **kwargs) -> tuple[bytes, bytes]:
        stdout = kwargs.get("stdout", PIPE)
        stderr = kwargs.get("stderr", PIPE)
        process = await asyncio.create_subprocess_exec(*args, stdout=stdout, stderr=stderr)
        return await process.communicate()

    @classmethod
    async def create_container(cls, port: int) -> bool:
        match config.get("GPU").casefold():
            case "nvidia":
                return not (await cls.run(*Commands.run_nvidia(port)))[1]
            case "amd":
                return not (await cls.run(*Commands.run_amd(port)))[1]
            case _:
                return not (await cls.run(*Commands.run_cpu(port)))[1]

    @classmethod
    async def get_containers(cls) -> list[str]:
        out, _ = await cls.run(*Commands.get_containers)
        return out.decode().replace("ollama", "")

    @classmethod
    async def check_container(cls, port: int) -> bool:
        out, _ = await cls.run(*Commands.check_container(port))
        return bool(out)

    @classmethod
    async def start_container(cls, port: int) -> bool:
        return not (await cls.run(*Commands.start(port)))[1]

    @classmethod
    async def stop_container(cls, port: int) -> bool:
        return not (await cls.run(*Commands.stop(port)))[1]

    @classmethod
    async def delete_container(cls, port: int) -> bool:
        if not await cls.stop_container(port):
            return False
        return not (await cls.run(*Commands.remove(port)))[1]

    @classmethod
    async def _load_model(cls, port: int, model: str) -> str:
        return await cls.run(*Commands.run(port), model)

    @classmethod
    async def prepare_container(cls, port: int, model: str) -> bool:
        _, error = await cls._load_model(port, model)

        if "No such container" in error.decode():
            return False

        if not "is not running" in error.decode():
            return True

        logging.info(f"Container ollama{port} suspended, restarting...")

        if not await cls.start_container(port):
            return False

        _, error = await cls._load_model(port, model)
        return error
