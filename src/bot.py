import asyncio
from loader import bot, dp
from aiogram.types.bot_command import BotCommand
from ollama_bot.handlers import default, language, models, gpt


async def set_commands():
    await bot.set_my_commands([
        BotCommand(command="stop", description="🚫"),
        BotCommand(command="clear", description="🧹"),
        BotCommand(command="help", description="❓"),
        BotCommand(command="set_model", description="🤖"),
        BotCommand(command="set_language", description="🌍"),
    ])


async def main() -> None:
    await set_commands()
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt as _:
        ...
