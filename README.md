# TG_LLAMA_GPT_SERVICE

#### Telegram bot based on ollama service integration.

### This project is using
- Aiogram
- Postgres (Sqlalchemy + alembic)
- Ollama

### Requirements:
- Docker
- python >= 3.8

---

#### Set up your BOT_TOKEN environment variable (you can get it from @BotFather)

---

## Installation

### Clone repo
```bash
git clone https://github.com/VEGAMETA/TG_LLAMA_GPT_SERVICE.git
cd TG_LLAMA_GPT_SERVICE
```

### Run python startup script
```bash
python startup.py
```

## Settings

Specify the desired model(s) in the `config.yml`. You can use any [availible model](https://ollama.com/library). Also you can change your GPU (by now ollama provides AMD support for linux only) or use CPU Don't forget to set up yout drivers (you can read [small guide](https://hub.docker.com/r/ollama/ollama) on the ollama's docker page). Be prepared to wait a while until required models are pulled.

---

##### If you are using Windows and just removed huge model don't forget to optimize your disc image.
```powershell
Optimize-VHD -Path "P:\path\to\your\DockerDesktop\vhdx\DockerDesktopWSL\data\ext4.vhdx"
```