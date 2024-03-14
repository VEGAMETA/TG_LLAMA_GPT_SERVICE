from aiogram import F
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart, Command

from loader import dp
from ollama_bot.states.user import UserState
from ollama_bot.models.user import User
from ollama_bot.models.language import Languages
from ollama_bot.misc.commands import commands, commands_f
from ollama_bot.keyboards.reply.default import get_default_keyboard


@dp.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    """
    CommandStart handler that sends a greeting message.
    """
    await state.set_state(UserState.chatting)
    user_id = message.from_user.id
    user = await User.get_user_by_id(user_id)
    if user:
        language = await Languages.get_dict_by_name(user.language)
        answer = language.get("restart")
    else:
        user = await User.create_user(user_id)
        language = await User.get_language(user_id)
        answer = language.get("greeting") + hbold(message.from_user.full_name) + language.get("start")
    await message.answer(answer, reply_markup=get_default_keyboard(language))


@dp.message(Command("cancel"))
@dp.message(F.text.in_(commands.get("cancel")))
async def cancel_handler(message: Message, state: FSMContext) -> None:
    """
    Allows user to cancel any action by resetting state.
    """
    current_state = await state.get_state()
    if current_state == UserState.chatting:
        return

    await state.set_state(UserState.chatting)
    user = await User.get_user_by_id(message.from_user.id)
    language = await Languages.get_dict_by_name(user.language)
    answer = language.get('canceled')
    await message.answer(answer, reply_markup=get_default_keyboard(language))


@dp.message(Command("help"))
@dp.message(F.text.in_(commands.get("command_help")))
async def help_handler(message: Message) -> None:
    """
    Help command handler (sends list of avalible commands).
    """
    user = await User.get_user_by_id(message.from_user.id)
    language = await Languages.get_dict_by_name(user.language)
    answer = language.get('help')
    await message.answer(answer + commands_f)
