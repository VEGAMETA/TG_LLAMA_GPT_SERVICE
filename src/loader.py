import sys
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.utils.token import TokenValidationError
from aiogram.utils.chat_action import ChatActionMiddleware
from aiogram.utils.callback_answer import CallbackAnswerMiddleware
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from ollama_bot.config import load_config
from ollama_bot.middlwares.database import DbSessionMiddleware
from ollama_bot.handlers import default, language, models, subscription, gpt

logging.basicConfig(
    format='%(asctime)s [%(levelname)s] - %(message)s',
    level=logging.INFO,
    stream=sys.stdout
)

config = load_config()

config.db.base_url = config.db.user + ":" + config.db.password + "@" + \
    config.db.host + ":" + str(config.db.port) + "/" + config.db.database
config.db.url = f"postgresql+asyncpg://{config.db.base_url}"

try:
    bot = Bot(token=config.tg_bot.token, parse_mode=ParseMode.HTML)
except TokenValidationError:
    logging.error("Invalid token")

engine = create_async_engine(url=config.db.url, echo=True)
sessionmaker = async_sessionmaker(engine, expire_on_commit=False)

dp = Dispatcher()
dp.update.middleware(DbSessionMiddleware(session_pool=sessionmaker))
dp.message.middleware(ChatActionMiddleware())
dp.callback_query.middleware(CallbackAnswerMiddleware())

dp.include_routers(default.router, language.router, models.router, subscription.router, gpt.router)
