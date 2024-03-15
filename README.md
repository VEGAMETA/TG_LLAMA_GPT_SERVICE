# TG_LLAMA_GPT_SERVICE

Telegram bot based on ollama service integration.

This project is using Aiogram, Postgres and Ollama

---

#### Set up your BOT_TOKEN environment variable (you can get it from @BotFather)

---

## Installation

### Clone repo
```bash
git clone https://github.com/VEGAMETA/TG_LLAMA_GPT_SERVICE.git
cd TG_LLAMA_GPT_SERVICE
```

### Docker
Build image
```bash
docker-compose build
```

Run service
```bash
docker-compose up
```

You can read little [docker manual](https://hub.docker.com/r/ollama/ollama) for ollama to set up your drivers. You can also  change your GPU (by now linux only supports AMD) or use CPU at
config.yml and feel free to modify models section but prepare 
to wait a lot until required models downloaded.

Stop service
```bash
docker-compose down
```

Remove invalid images 
```bash
docker rmi -f $(docker images -f "dangling=true" -q)
```