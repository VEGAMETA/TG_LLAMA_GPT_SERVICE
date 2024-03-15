import asyncio
import urllib.parse
from container_handler.containers import create_container

class Server:

    def __init__(self, host:str='localhost', port:int=11433) -> None:
        self.host = host
        self.port = port
    
    async def start(self):
        server = await asyncio.start_server(self.handle_request, '127.0.0.1', 23157)
        addr = server.sockets[0].getsockname()
        print(f'Serving on {addr}')
        async with server:
            await server.serve_forever()

    async def handle_request(self, reader, writer):
        data = await reader.read()
        message = data.decode()

        parsed = urllib.parse.urlparse(message.splitlines()[0])
        query = urllib.parse.parse_qs(parsed.query)
        
        match parsed.path:
            case '/run_container':
                response, status_code = await self.run_container(query)
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

    async def run_container(self, query):
            if not  {'port', 'model'}.issubset(query):
                return "Invalid request, port and model parameters are required", 400

            port = query.get('port')[0]
            model = query.get('model')[0]

            try:
                port = int(port)
            except ValueError:
                return "Invalid request, port must be an integer", 400

            if port not in range(1025, 65536):
                return "Invalid request, port must be between 1025 and 65535", 400
            
            docker_response = create_container(port, model)
            
            if docker_response.endswith("port is already allocated"):
                return "Port is already allocated (not by container)", 409
                
            if "is already in use by container" in docker_response:
                return "Port is already in use by another container", 409
            
            ...
            
            return f"Starting container at port {port} and model {model}", 201

server = Server()
asyncio.run(server.start())
