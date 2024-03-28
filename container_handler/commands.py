class Commands:
    up = "docker-compose up -d".split()
    down = "docker-compose down".split()
    build = "docker-compose build".split()
    remove_images = "docker rmi -f".split()
    remove_containers = "docker rm -f".split()
    get_dangling = "docker images -f dangling=true -q".split()
    create_network = "docker network create tg_bot_network".split()
    get_containers = "docker ps -a --filter name=ollama\d+$ --format {{.Names}}".split()

    @staticmethod
    def remove(port) -> list[str]:
        return f"docker rm ollama{port}".split()

    @staticmethod
    def stop(port) -> list[str]:
        return f"docker stop ollama{port}".split()

    @staticmethod
    def stop_container(port) -> list[str]:
        return f"docker stop ollama{port}".split()

    @staticmethod
    def start(port) -> list[str]:
        return f"docker start ollama{port}".split()

    @staticmethod
    def run(port) -> list[str]:
        return f"docker exec ollama{port} ollama run".split()

    @staticmethod
    def pull(puller_name):
        return f"docker exec ollama{puller_name} ollama pull".split()

    @staticmethod
    def check_container(port) -> list[str]:
        return f"docker ps -a --filter name=ollama{port} --format '{{{{.Names}}}}'".split()

    def run_puller(puller_name) -> list[str]:
        return f"docker run -d -v tg_llama_gpt_service_llm-service:/root/.ollama --name ollama{puller_name}".split()

    @staticmethod
    def run_cpu(port) -> list[str]:
        return f"docker run -d --name ollama{port} -p {port}:11434 --network tg_bot_network -v tg_llama_gpt_service_llm-service:/root/.ollama ollama/ollama:0.1.30-rc4".split()

    @staticmethod
    def run_nvidia(port) -> list[str]:
        return f"docker run -d --gpus=all --name ollama{port} -p {port}:11434 --network tg_bot_network -v tg_llama_gpt_service_llm-service:/root/.ollama ollama/ollama:0.1.30-rc4".split()

    @staticmethod
    def run_amd(port) -> list[str]:
        return f"docker run -d --device /dev/kfd --device /dev/dri --name ollama{port} -p {port}:11434 --network tg_bot_network -v tg_llama_gpt_service_llm-service:/root/.ollama ollama/ollama:0.1.30-rc4-rocm".split()
