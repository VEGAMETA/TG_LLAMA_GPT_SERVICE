from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from project_config import models
from ollama_bot.misc.language import get_language
from ollama_bot.models.user import User
from ollama_bot.states.user import UserState
from ollama_bot.misc.commands import commands
from ollama_bot.keyboards.reply.models import get_model_keyboard
from ollama_bot.keyboards.reply.default import get_default_keyboard

router = Router(name="models-commands-router")

@router.message(Command("set_model"))
@router.message(F.text.in_(commands.get("command_set_model")))
async def model_change_handler(message: Message, state: FSMContext, session: AsyncSession) -> None:
    """
    Handles model change.
    """
    await state.set_state(UserState.choosing_model)
    user = await session.get(User, message.from_user.id)
    language = await get_language(user.language)
    answer = language.get('set_model')
    await message.answer(answer, reply_markup=get_model_keyboard(language))


@router.message(UserState.choosing_model)
async def set_model_handler(message: Message, state: FSMContext, session: AsyncSession) -> None:
    """
    Handles model set.
    """
    await state.set_state(UserState.chatting)
    user = await session.get(User, message.from_user.id)
    language = await get_language(user.language)
    for model in models:
        if message.text == model:
            user.model = model
            session.commit()
            answer = language.get('set_model_after') + model
            await message.answer(answer, reply_markup=get_default_keyboard(language))
            return
    else:
        answer = language.get('error')
        await message.answer(answer, reply_markup=get_default_keyboard(language))
