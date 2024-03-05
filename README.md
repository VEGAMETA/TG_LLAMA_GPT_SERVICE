# TG_LLAMA_GPT_SERVICE

Telegram bot based on ollama service integration.

This project is using Aiogram, Postgres and Ollama


---

### Docker
Build image
```bash
docker-compose build
```

Run service
```bash
docker-compose up
```

#### Do not forget to pull needed [model(s)](https://ollama.com/library) at ollama container
```bash
ollama pull llama2
```

Stop service
```bash
docker-compose down
```

Remove invalid images 
```bash
docker rmi $(docker images -f "dangling=true" -q)
```