import asyncio
from loader import bot, dp, init_tables
from aiogram.types.bot_command import BotCommand


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
    await init_tables()
    await set_commands()
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt as _:
        ...
