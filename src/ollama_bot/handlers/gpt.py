import time
import json
import logging
import asyncio
import aiohttp
import aiogram.exceptions
import aiohttp.client_exceptions
from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from project_config import models
from ollama_bot.models.user import User
from ollama_bot.misc.markdown import escape
from ollama_bot.states.user import UserState
from ollama_bot.misc.commands import commands
from ollama_bot.misc.language import get_language
from ollama_bot.misc.containers import get_container_port, unoperate

router = Router(name="gpt-commands-router")


@router.message(Command("stop"))
@router.message(F.text.in_(commands.get("command_stop")))
async def stop_handler(message: Message, session: AsyncSession) -> None:
    """
    Request for gpt to stop answering
    """
    user = await session.get(User, message.from_user.id)
    user.processing = False
    await session.commit()


@router.message(Command("clear"))
@router.message(F.text.in_(commands.get("command_clear")))
async def clear_handler(message: Message, session: AsyncSession) -> None:
    """
    Clears the context for user gpt request
    """
    user = await session.get(User, message.from_user.id)
    user.context = []
    await session.commit()
    language = await get_language(user.language)
    answer = language.get('clear')
    await message.answer(answer)


@router.message(F.text)
async def gpt_handler(message: Message, state: FSMContext, session: AsyncSession) -> None:
    """
    This handler manage ollama gpt api calls with streaming and editing message for it.
    """
    current_state = await state.get_state()
    if current_state not in (UserState.chatting, None):
        return

    user_id: int = message.from_user.id
    user = await session.get(User, user_id)
    if not user:
        await session.merge(User(user_id=user_id))
        await session.commit()
    user = await session.get(User, user_id)

    language = await get_language(user.language)

    if user.processing:
        answering = language.get('answering')
        await message.answer(answering)
        return

    user.processing = True
    await session.commit()
    bot_message = await message.answer('•••', parse_mode="MarkdownV2")
    network_error = False
    bot_message_time = time.monotonic()
    answer = ''
    data = {
        "prompt": message.text,
        "model": models[user.model],
        "context": user.context,
    }

    port = await get_container_port(session, user.model)
    response = ''
    not_escaped_answer = ''
    raw_message = b''
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60*15)) as client_session:
            from loader import config
            async with client_session.post(f'http://{config.db.host}:{port}/api/generate', json=data) as response:
                async for chunk in response.content.iter_chunks():
                    try:
                        if not isinstance(chunk, tuple):
                            error = language.get("error_empty")
                            await bot_message.edit_text(answer + error, parse_mode="MarkdownV2")
                            return
                        
                        raw_message += chunk[0]
                        if not chunk[1]:
                            continue
                        
                        resp_json = json.loads(raw_message.decode())

                        raw_message = b''

                        # Getting response and formatting
                        response = resp_json.get("response")
                        not_escaped_answer += response
                        answer = await escape(not_escaped_answer)

                        # End of response, writing context
                        if resp_json.get("done"):
                            await bot_message.edit_text(answer, parse_mode="MarkdownV2")
                            context = resp_json.get("context")
                            user.context = context
                            await session.commit()
                            return

                        await session.refresh(user)
                        if not user.processing:
                            error = language.get("stopped")
                            await bot_message.edit_text(answer + error, parse_mode="MarkdownV2")
                            return

                        # Delay editing to avoid api requests excesses
                        if time.monotonic() - bot_message_time > 3:
                            await bot_message.edit_text(answer, parse_mode="MarkdownV2")
                            bot_message_time = time.monotonic()

                    # Json error handler
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
                            bot_message_time = time.monotonic()
                            continue
                        if "Bad Request: can't parse entities" in e.message:
                            await bot_message.edit_text(not_escaped_answer)
                            bot_message_time = time.monotonic()
                            continue

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
        await unoperate(session, port)
        user.processing = False
        await session.commit()
