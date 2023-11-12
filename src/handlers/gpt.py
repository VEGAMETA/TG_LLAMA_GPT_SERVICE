import time
import json
import logging
import asyncio
import aiohttp
import aiogram
import aiogram.exceptions
from loader import dp


@dp.message(aiogram.F.text)
async def gpt_handler(message: aiogram.types.Message) -> None:
    """
    This handler manage ollama gpt api calls with streaming and editing message for it.
    """
    data = {
        "model": "llama2", # message.from_user.id.get_model()
        "prompt": message.text,
        
        # "context": message.from_user.id.get_context(),
    }
    bot_message = await message.answer('•••')
    text = ''
    bot_message_time = time.monotonic()
    async with aiohttp.ClientSession() as session:
        async with session.post('http://127.0.0.1:11434/api/generate', json=data) as response:
            async for resp in response.content.iter_chunks():
                try:
                    resp_json = json.loads(resp[0].decode('utf-8'))
                    text += resp_json.get('response')
                    if resp_json.get('done'):
                        await bot_message.edit_text(text)
                        logging.info(f'{resp_json.get("context")}')
                        return
                    if time.monotonic() - bot_message_time > 3:
                        await bot_message.edit_text(text)
                        bot_message_time = time.monotonic()
                except json.decoder.JSONDecodeError as e:
                    await bot_message.edit_text(text)
                    return logging.error(e)
                except aiogram.exceptions.TelegramBadRequest as e:
                    logging.error(e)
                except aiogram.exceptions.TelegramRetryAfter as e:
                    logging.error(e)
                    await asyncio.sleep(e.retry_after)
