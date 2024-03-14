import asyncio
from ollama_bot.models import User, Transaction
from loader import bot, dp, db
from aiogram.types.bot_command import BotCommand
from ollama_bot.handlers import default, language, models, subscription, gpt


async def set_commands():
    """
    Set commands for menu.
    """
    await bot.set_my_commands([
        BotCommand(command="stop", description="🚫"),
        BotCommand(command="clear", description="🧹"),
        BotCommand(command="help", description="❓"),
        BotCommand(command="set_model", description="🤖"),
        BotCommand(command="set_language", description="🌍"),
    ])


async def main() -> None:
    await set_commands()
    # await db.migrate() no need (alembic is using)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    except KeyboardInterrupt as _:
        ...
