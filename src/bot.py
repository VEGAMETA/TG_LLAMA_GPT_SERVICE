import asyncio
from loader import bot, dp
from ollama_bot.handlers import default, gpt


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt as _:
        ...
