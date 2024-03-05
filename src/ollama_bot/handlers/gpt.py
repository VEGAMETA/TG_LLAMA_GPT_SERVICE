import time
import json
import logging
import asyncio
import aiohttp
import aiogram
import aiogram.exceptions
import aiohttp.client_exceptions
from aiogram.fsm.context import FSMContext

from ollama_bot.misc.gpt import RequestStatus
from ollama_bot.models.user import User, users
from loader import dp
from ollama_bot.states.user import UserState


@dp.message(aiogram.F.text)
async def gpt_handler(message: aiogram.types.Message, state: FSMContext) -> None:
    """
    This handler manage ollama gpt api calls with streaming and editing message for it.
    """
    current_state = await state.get_state()
    if current_state != UserState.chatting:
        return

    user_id: int = message.from_user.id
    user = users.get(user_id) if user_id in users.keys(
    ) else User.create_user(user_id)

    if user.request_status == RequestStatus.PROCESSING:
        await message.answer('Previous request is processing\nCall /stop to stop answering')
        return

    user.request_status = RequestStatus.PROCESSING
    bot_message = await message.answer('•••')
    network_error = False
    bot_message_time = time.monotonic()
    answer = ''
    data = {
        "prompt": message.text,
        "model": users.get(user_id).model.value,
        "context": users.get(user_id).context,
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post('http://192.168.1.100:11434/api/generate', json=data) as response:
                async for chunk in response.content.iter_chunks():
                    try:
                        if not isinstance(chunk, tuple):
                            await bot_message.edit_text(answer + "...\n\n(Technical issues)\nAnswer is empty")
                            return

                        # User's stop request handler
                        if users.get(user_id).request_status == RequestStatus.STOP_REQUEST:
                            await bot_message.edit_text(answer + "...\n\nRequest stopped by user")
                            return

                        resp_json = json.loads(chunk[0].decode('utf-8'))
                        answer += resp_json.get('response')

                        # End of response, writing context
                        if resp_json.get('done'):
                            await bot_message.edit_text(answer)
                            users.get(user_id).context = resp_json.get(
                                "context")
                            return

                        # Delay editing to avoid api requests excesses
                        if time.monotonic() - bot_message_time > 3:
                            await bot_message.edit_text(answer)
                            bot_message_time = time.monotonic()

                    # Json error handler (ignore?)
                    except json.decoder.JSONDecodeError as e:
                        logging.error(e)
                        await bot_message.edit_text(answer)
                        return

                    # Bad request error handler (how to handle other types?)
                    except aiogram.exceptions.TelegramBadRequest as e:
                        logging.error(e)
                        if e.message == "Bad Request: message to edit not found":
                            return

                    # Simple retry after error handler (waiting)
                    except aiogram.exceptions.TelegramRetryAfter as e:
                        logging.error(e)
                        await asyncio.sleep(e.retry_after)

                    except aiogram.exceptions.TelegramNetworkError as e:
                        logging.error(e)
                        if network_error:
                            return
                        network_error = True
                        await asyncio.sleep(3)

                    except aiohttp.client_exceptions.ClientConnectorError as e:
                        logging.error(e)
                        await bot_message.edit_text(answer + "...\n\n(Technical issues)\nClient Connector Error")

    except asyncio.exceptions.TimeoutError as _:
        await bot_message.edit_text(answer + "...\n\nTimeout Error (>5min)")

    except aiohttp.client_exceptions.ServerDisconnectedError as e:
        logging.error(e)
        await bot_message.edit_text(answer + "...\n\n(Technical issues)\nServer disconnected")

    finally:
        users.get(user_id).request_status = RequestStatus.NONE
