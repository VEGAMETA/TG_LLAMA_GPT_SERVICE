import asyncio
import logging
import functools
from urllib.parse import parse_qs, urlparse
from asyncio.streams import StreamReader, StreamWriter, _DEFAULT_LIMIT
from src.project_config import config
from container_handler.containers import ContainerHandler


def with_params(*check_params):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(self, params, *args, **kwargs):
            processed_params = []
            for param in check_params:
                if param not in params:
                    return f"Invalid request, {param} parameter is required", 400
                processed_params.append(params.get(param))
            return await func(self, *processed_params, *args, **kwargs)
        return wrapper
    return decorator


def validate_port(func):
    @functools.wraps(func)
    async def wrapper(self, port, *args, **kwargs):
        try:
            port = int(port)
        except ValueError:
            return "Invalid request, port must be an integer", 400
        if port not in range(1025, 65536):
            return "Invalid request, port must be between 1025 and 65535", 400
        return await func(self, port, *args, **kwargs)
    return wrapper


class Server:

    def __init__(
        self,
        host: str = '127.0.0.1',
        port: int = int(config.get('CONTAINER_HANDLER_SERVER_PORT', 11433))
    ) -> None:
        self.host = host
        self.port = port

    async def _start(self) -> None:
        server = await asyncio.start_server(self._handle_request, self.host, self.port)
        addr = server.sockets[0].getsockname()
        logging.info(f'Serving on {addr}')
        async with server:
            await server.serve_forever()

    async def _handle_request(self, reader: StreamReader, writer: StreamWriter) -> None:
        data = await reader.read(_DEFAULT_LIMIT)
        message = data.decode()
        parsed = urlparse(message.split('\n')[0].split(' ')[1])
        function = parsed.path[1:]
        params = {k: v[0] for k, v in parse_qs(parsed.query).items()}

        if callable(getattr(self, function)) and not function.startswith("_"):
            response, status_code = await getattr(self, function)(params)
        else:
            response, status_code = "Invalid request", 404

        response_headers = (
            f'HTTP/1.1 {status_code}\r\n'
            'Content-Type: text/plain; charset=utf-8\r\n'
            f'Content-Length: {len(response)}\r\n'
            'Connection: close\r\n'
            '\r\n'
            f'{response}'
        )

        writer.write(response_headers.encode())
        await writer.drain()
        writer.close()
        await writer.wait_closed()

    async def get_containers(self, _) -> tuple[str, int]:
        ports = await ContainerHandler.get_containers()
        if not ports:
            return "No containers found", 404
        return ports, 200

    async def start_containers(self, _) -> tuple[str, int]:
        ports = await ContainerHandler.get_containers()
        if not ports:
            return "No containers found", 404
        for port in ports.split('\n')[:-1]:
            asyncio.create_task(ContainerHandler.start_container(port))
        return ports, 200

    @with_params("port")
    @validate_port
    async def check_container(self, port) -> tuple[str, int]:
        if not await ContainerHandler.check_container(port):
            return "Container is not running", 404
        await ContainerHandler.start_container(port)
        return "Container is running", 200

    @with_params("port", "model")
    @validate_port
    async def create_container(self, port, model) -> tuple[str, int]:
        if not await ContainerHandler.create_container(port):
            return "Port is already allocated", 409
        if not await ContainerHandler.prepare_container(port, model):
            return "Failed to prepare container", 500
        return f"Starting container at port {port} and model {model}", 201

    @with_params("port", "model")
    @validate_port
    async def start_container(self, port, model) -> tuple[str, int]:
        if port not in range(1025, 65536):
            return "Invalid request, port must be between 1025 and 65535", 400
        if not await ContainerHandler.prepare_container(port, model):
            return "Failed to prepare container", 500
        return f"Starting container at port {port} and model {model}", 201

    @with_params("port")
    @validate_port
    async def stop_container(self, port) -> tuple[str, int]:
        if not await ContainerHandler.stop_container(port):
            return "Failed to stop container", 500
        return f"Stopping container at port {port}", 200

    @with_params("port")
    @validate_port
    async def delete_container(self, port) -> tuple[str, int]:
        if not await ContainerHandler.delete_container(port):
            return "Failed to delete container", 500
        return "", 204
