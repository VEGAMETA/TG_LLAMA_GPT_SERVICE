from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from ollama_bot.models.user import User
from ollama_bot.states.user import UserState
from ollama_bot.misc.commands import commands
from ollama_bot.misc.language import get_language, Languages
from ollama_bot.keyboards.reply.default import get_default_keyboard
from ollama_bot.keyboards.reply.language import get_language_keyboard

router = Router(name="language-commands-router")

@router.message(Command("set_language"))
@router.message(F.text.in_(commands.get("command_set_language")))
async def langugage_change_handler(message: Message, state: FSMContext, session: AsyncSession) -> None:
    """
    Handles language change.
    """
    await state.set_state(UserState.choosing_language)
    user = await session.get(User, message.from_user.id)
    language = await get_language(user.language)
    answer = language.get('set_language')
    await message.answer(answer, reply_markup=get_language_keyboard(language))


@router.message(UserState.choosing_language)
async def set_language_handler(message: Message, state: FSMContext, session: AsyncSession) -> None:
    """
    Handles language set.
    """
    await state.set_state(UserState.chatting)
    user = await session.get(User, message.from_user.id)
    user_language = await get_language(user.language)
    for language in Languages:
        if message.text == language.value.name:
            user.language = language.name
            await session.commit()
            answer = language.value.dictionary.get('set_language_after')
            await message.answer(answer, reply_markup=get_default_keyboard(language.value.dictionary))
            return
    else:
        answer = user_language.get('error')
        await message.answer(answer, reply_markup=get_default_keyboard(user_language))
