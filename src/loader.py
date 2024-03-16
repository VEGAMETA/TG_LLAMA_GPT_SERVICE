import sys
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.utils.token import TokenValidationError
from aiogram.fsm.storage.memory import MemoryStorage
from ollama_bot.config import load_config
from ollama_bot.misc.database import Database

logging.basicConfig(
    format='%(asctime)s [%(levelname)s] - %(message)s',
    level=logging.INFO,
    stream=sys.stdout
)

config = load_config()

try:
    bot = Bot(token=config.tg_bot.token, parse_mode=ParseMode.HTML)
except TokenValidationError:
    print("Invalid token")

storage = MemoryStorage()
dp = Dispatcher(storage=storage)

config.db.base_url = f"{config.db.user}:{config.db.password}@{config.db.host}:{config.db.port}/{config.db.database}"
config.db.url = f"postgresql+asyncpg://{config.db.base_url}"
db = Database(config.db.url)
