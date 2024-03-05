from ollama_bot.misc.gpt import Models


class Container:
    def __init__(self) -> None:
        self.id: int = 0
        self.ip: str = ''
        self.available_models: list[Models] = []
        self.available_ram: int = 0
        self.inner_port: int = 0
        self.outer_port: int = 0
        self.is_operating: bool = False
