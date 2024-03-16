import logging
import asyncio
import urllib.parse
from asyncio.streams import StreamReader, StreamWriter, _DEFAULT_LIMIT
from container_handler.project_config import config
from container_handler.containers import ContainerHandler


class Server:

    def __init__(
        self,
        host: str = '127.0.0.1',
        port: int = int(config.get('CONTAINER_HANDLER_SERVER_PORT', 11433))
    ) -> None:
        self.host = host
        self.port = port

    async def start(self) -> None:
        server = await asyncio.start_server(self.handle_request, self.host, self.port)
        addr = server.sockets[0].getsockname()
        logging.info(f'Serving on {addr}')
        async with server:
            await server.serve_forever()

    async def handle_request(self, reader: StreamReader, writer: StreamWriter) -> None:
        data = await reader.read(_DEFAULT_LIMIT)
        message = data.decode()
        parsed = urllib.parse.urlparse(message.split('\n')[0].split(' ')[1])
        params = {k: v[0] for k, v in urllib.parse.parse_qs(parsed.query).items()}

        match parsed.path:
            case '/create_container':
                response, status_code = await self.create_container(params)
            case '/start_container':
                response, status_code = await self.start_container(params)
            case '/stop_container':
                response, status_code = await self.stop_container(params)
            case '/delete_container':
                response, status_code = await self.delete_container(params)
            case _:
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

    async def create_container(self, params) -> tuple[str, int]:
        if not {'port', 'model'}.issubset(params):
            return "Invalid request, port and model parameters are required", 400

        port = params.get('port')
        model = params.get('model')

        try:
            port = int(port)
        except ValueError:
            return "Invalid request, port must be an integer", 400

        if port not in range(1025, 65536):
            return "Invalid request, port must be between 1025 and 65535", 400

        if not await ContainerHandler.create_container(port):
            return "Port is already allocated", 409

        if not await ContainerHandler.prepare_container(port, model):
            return "Failed to prepare container", 500

        return f"Starting container at port {port} and model {model}", 201

    async def start_container(self, params) -> tuple[str, int]:
        if not {'port', 'model'}.issubset(params):
            return "Invalid request, port and model parameters are required", 400

        port = params.get('port')
        model = params.get('model')

        try:
            port = int(port)
        except ValueError:
            return "Invalid request, port must be an integer", 400

        if port not in range(1025, 65536):
            return "Invalid request, port must be between 1025 and 65535", 400

        if not await ContainerHandler.prepare_container(port, model):
            return "Failed to prepare container", 500

        return f"Starting container at port {port} and model {model}", 201

    async def stop_container(self, params) -> tuple[str, int]:
        if 'port' not in params:
            return "Invalid request, port parameter is required", 400

        port = params.get('port')

        try:
            port = int(port)
        except ValueError:
            return "Invalid request, port must be an integer", 400

        if port not in range(1025, 65536):
            return "Invalid request, port must be between 1025 and 65535", 400

        if not await ContainerHandler.stop_container(port):
            return "Failed to stop container", 500

        return f"Stopping container at port {port}", 200

    async def delete_container(self, params) -> tuple[str, int]:
        if 'port' not in params:
            return "Invalid request, port parameter is required", 400

        port = params.get('port')

        try:
            port = int(port)
        except ValueError:
            return "Invalid request, port must be an integer", 400

        if port not in range(1025, 65536):
            return "Invalid request, port must be between 1025 and 65535", 400

        if not await ContainerHandler.delete_container(port):
            return "Failed to delete container", 500

        return f"Deleting container at port {port}", 200  # Maybe 204
