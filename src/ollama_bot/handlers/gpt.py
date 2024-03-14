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
from ollama_bot.misc.gpt import Models
from ollama_bot.models.language import Languages
from ollama_bot.states.user import UserState
from ollama_bot.misc.commands import commands
from ollama_bot.models.user import User
from ollama_bot.keyboards.reply.default import get_default_keyboard

special_chars = ('_', '*', '[', ']', '(', ')', '~', '`',
                 '>', '#', '+', '-', '=', '|', '{', '}', '.', '!')


@dp.message(Command("stop"))
@dp.message(F.text.in_(commands.get("command_stop")))
async def stop_handler(message: Message) -> None:
    """
    Request for gpt to stop answering
    """
    await User.set_processing(message.from_user.id, False)

@dp.message(Command("clear"))
@dp.message(F.text.in_(commands.get("command_clear")))
async def clear_handler(message: Message) -> None:
    """
    Clears the context for user gpt request
    """
    user_id = message.from_user.id
    user = await User.get_user_by_id(message.from_user.id)
    await User.set_context(user_id, [])
    language = await Languages.get_dict_by_name(user.language)
    answer = language.get('clear')
    await message.answer(answer, reply_markup=get_default_keyboard(language))


@dp.message(F.text)
async def gpt_handler(message: Message, state: FSMContext) -> None:
    """
    This handler manage ollama gpt api calls with streaming and editing message for it.
    """
    current_state = await state.get_state()
    if current_state != UserState.chatting:
        return

    user_id: int = message.from_user.id
    user = await User.get_user_by_id(user_id)
    if not user:
        await User.create_user(user_id)
        user = await User.get_user_by_id(user_id)

    language = await Languages.get_dict_by_name(user.language)

    if user.processing:
        answering = language.get('answering')
        await message.answer(answering)
        return

    await User.set_processing(user_id, True)
    bot_message = await message.answer('•••', parse_mode="MarkdownV2")
    network_error = False
    bot_message_time = time.monotonic()
    answer = ''
    data = {
        "prompt": message.text,
        "model": Models.get_model_by_name(user.model),
        "context": user.context,
    }

    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60*15)) as session:
            async with session.post('http://host.docker.internal:11434/api/generate', json=data) as response:
                async for chunk in response.content.iter_chunks():
                    try:
                        if not isinstance(chunk, tuple):
                            error = language.get("error_empty")
                            await bot_message.edit_text(answer + error, parse_mode="MarkdownV2")
                            return

                        # User's stop request handler
                        if not await User.get_processing(user_id):
                            error = language.get("stopped")
                            await bot_message.edit_text(answer + error, parse_mode="MarkdownV2")
                            return

                        # Getting response and formatting
                        resp_json = json.loads(chunk[0].decode("utf-8"))
                        response = resp_json.get("response")
                        for special_char in special_chars:
                            response = response.replace(
                                special_char, f"\\{special_char}")
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
                            context = resp_json.get("context")
                            await User.set_context(user_id, context)
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
                        error = language.get("error_connect")
                        await bot_message.edit_text(answer + error, parse_mode="MarkdownV2")

                    except asyncio.exceptions.TimeoutError as _:
                        error = language.get("error_timeout")
                        await bot_message.edit_text(answer + error, parse_mode="MarkdownV2")

    except aiohttp.client_exceptions.ServerDisconnectedError as e:
        logging.error(e)
        error = language.get("error_server")
        await bot_message.edit_text(answer + error, parse_mode="MarkdownV2")

    finally:
        await User.set_processing(user_id, False)
