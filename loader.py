import sys
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from src.config import load_config

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
storage = MemoryStorage()
config = load_config()
bot = Bot(token=config.tg_bot.token, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=storage)
