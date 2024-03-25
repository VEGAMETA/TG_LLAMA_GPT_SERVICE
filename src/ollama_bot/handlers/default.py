from aiogram import F, Router
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart, Command
from sqlalchemy.ext.asyncio import AsyncSession

from ollama_bot.states.user import UserState
from ollama_bot.models.user import User
from ollama_bot.misc.language import get_language
from ollama_bot.misc.commands import commands, commands_f
from ollama_bot.keyboards.reply.default import get_default_keyboard

router = Router(name="default-commands-router")

@router.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext, session: AsyncSession) -> None:
    """
    CommandStart handler that sends a greeting message.
    """
    await state.set_state(UserState.chatting)
    user_id = message.from_user.id
    user = await session.get(User, user_id)
    if user:
        language = await get_language(user.language)
        answer = language.get("restart")
    else:
        user = User(user_id=user_id)
        await session.merge(user)
        await session.commit()
        language = await get_language(user.language)
        answer = language.get("greeting") + hbold(message.from_user.full_name) + language.get("start")
    await message.answer(answer, reply_markup=get_default_keyboard(language))


@router.message(Command("cancel"))
@router.message(F.text.in_(commands.get("cancel")))
async def cancel_handler(message: Message, state: FSMContext, session: AsyncSession) -> None:
    """
    Allows user to cancel any action by resetting state.
    """
    current_state = await state.get_state()
    if current_state == UserState.chatting:
        return
    await state.set_state(UserState.chatting)
    user = await session.get(User, message.from_user.id)
    language = await get_language(user.language)
    answer = language.get('canceled')
    await message.answer(answer, reply_markup=get_default_keyboard(language))


@router.message(Command("help"))
@router.message(F.text.in_(commands.get("command_help")))
async def help_handler(message: Message, session: AsyncSession) -> None:
    """
    Help command handler (sends list of avalible commands).
    """
    user = await session.get(User, message.from_user.id)
    language = await get_language(user.language)
    answer = language.get('help')
    await message.answer(answer + commands_f)
