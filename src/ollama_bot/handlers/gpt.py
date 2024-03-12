import time
import json
import logging
import asyncio
import aiohttp
import aiogram.exceptions
import aiohttp.client_exceptions

from aiogram import F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from loader import dp
from ollama_bot.states.user import UserState
from ollama_bot.misc.commands import commands
from ollama_bot.misc.gpt import RequestStatus
from ollama_bot.models.user import User, users
from ollama_bot.keyboards.reply.default import get_default_keyboard

special_chars = ('_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!')

@dp.message(Command("stop"))
@dp.message(F.text.in_(commands.get("command_stop")))
async def stop_handler(message: Message) -> None:
    """
    Request for gpt to stop answering
    """
    user = users.get(message.from_user.id)
    user.request_status = RequestStatus.STOP_REQUEST


@dp.message(Command("clear"))
@dp.message(F.text.in_(commands.get("command_clear")))
async def clear_handler(message: Message) -> None:
    """
    Clears the context for user gpt request
    """
    user = users.get(message.from_user.id)
    user.context.clear()
    answer = user.language.value.dictionary.get('clear')
    await message.answer(answer, reply_markup=get_default_keyboard(user.language))


@dp.message(F.text)
async def gpt_handler(message: Message, state: FSMContext) -> None:
    """
    This handler manage ollama gpt api calls with streaming and editing message for it.
    """
    current_state = await state.get_state()
    if current_state != UserState.chatting:
        return

    user_id: int = message.from_user.id
    user = users.get(user_id) if user_id in users.keys() else User.create_user(user_id)

    if user.request_status == RequestStatus.PROCESSING:
        answering = user.language.value.dictionary.get('answering')
        await message.answer(answering)
        return

    user.request_status = RequestStatus.PROCESSING
    bot_message = await message.answer('•••', parse_mode="MarkdownV2")
    network_error = False
    bot_message_time = time.monotonic()
    answer = ''
    data = {
        "prompt": message.text,
        "model": users.get(user_id).model.value,
        "context": users.get(user_id).context,
    }

    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60*15)) as session:
            async with session.post('http://host.docker.internal:11434/api/generate', json=data) as response:
                async for chunk in response.content.iter_chunks():
                    try:
                        if not isinstance(chunk, tuple):
                            error = user.language.value.dictionary.get("error_empty")
                            await bot_message.edit_text(answer + error, parse_mode="MarkdownV2")
                            return

                        # User's stop request handler
                        if users.get(user_id).request_status == RequestStatus.STOP_REQUEST:
                            error = user.language.value.dictionary.get("stopped")
                            await bot_message.edit_text(answer + error, parse_mode="MarkdownV2")
                            return
                        
                        # Getting response and formatting
                        resp_json = json.loads(chunk[0].decode("utf-8"))
                        response = resp_json.get("response")
                        for special_char in special_chars:
                            response = response.replace(special_char, f"\\{special_char}")
                        answer += response
                        
                        # Formatting code blocks
                        if answer.count("\`\`\`"):
                            if answer.count("\`\`\`") % 2 == 0:
                                answer = answer.replace("\`\`\`", "```")
                        elif answer.count("\`") % 2 == 0:
                            answer = answer.replace("\`", "`")
                        

                        # End of response, writing context
                        if resp_json.get("done"):
                            await bot_message.edit_text(answer, parse_mode="MarkdownV2")
                            users.get(user_id).context = resp_json.get("context")
                            return

                        # Delay editing to avoid api requests excesses
                        if time.monotonic() - bot_message_time > 3:
                            await bot_message.edit_text(answer, parse_mode="MarkdownV2")
                            bot_message_time = time.monotonic()

                    # Json error handler (ignore?)
                    except json.decoder.JSONDecodeError as e:
                        logging.error(e)
                        await bot_message.edit_text(answer)
                        return

                    # Bad request error handler (how to handle other types?)
                    except aiogram.exceptions.TelegramBadRequest as e:
                        logging.error(e)
                        if "Bad Request: message to edit not found" in e.message:
                            return
                        if "Bad Request: message is not modified" in e.message:
                            continue
                        if "Bad Request: can't parse entities" in e.message:
                            await bot_message.edit_text(answer)

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
                        error = user.language.value.dictionary.get("error_connect")
                        await bot_message.edit_text(answer + error)

                    except asyncio.exceptions.TimeoutError as _:
                        error = user.language.value.dictionary.get("error_timeout")
                        await bot_message.edit_text(answer + error)

                    
    except aiohttp.client_exceptions.ServerDisconnectedError as e:
        logging.error(e)
        error = user.language.value.dictionary.get("error_server")
        await bot_message.edit_text(answer + error, parse_mode="Markdown")

    finally:
        users.get(user_id).request_status = RequestStatus.IDLE
