from aiogram import F
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart, Command

from loader import dp
from ollama_bot.states.user import UserState
from ollama_bot.misc.gpt import RequestStatus
from ollama_bot.misc.commands import commands
from ollama_bot.models.user import User, users
from ollama_bot.keyboards.reply.models import get_model_keyboard
from ollama_bot.keyboards.reply.default import get_default_keyboard



@dp.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    """
    CommandStart handler that sends a greeting message.
    """
    await state.set_state(UserState.chatting)
    user_id = message.from_user.id
    if user_id in users.keys():
        user = users[user_id]
        user.request_status = RequestStatus.IDLE
        answer = user.language.value.dictionary.get("restart")
        await message.answer(answer, reply_markup=get_default_keyboard(user.language))
        return
    user = User.create_user(user_id)
    user_name = message.from_user.full_name
    answer = user.language.value.dictionary.get("greeting") + hbold(user_name) + user.language.value.dictionary.get("start")
    await message.answer(answer,reply_markup=get_default_keyboard(user.language))

@dp.message(Command("cancel"))
@dp.message(F.text.in_(commands.get("cancel")))
async def cancel_handler(message: Message, state: FSMContext) -> None:
    """
    Allows user to cancel any action
    """
    current_state = await state.get_state()
    if current_state == UserState.chatting:
        return

    await state.set_state(UserState.chatting)
    user = users.get(message.from_user.id)
    answer = user.language.value.dictionary.get('canceled')
    await message.answer(answer, reply_markup=get_default_keyboard(user.language))


@dp.message(Command("help"))
@dp.message(F.text.in_(commands.get("command_help")))
async def help_handler(message: Message) -> None:
    """
    Help command handler sends list of commands
    """
    commands: str = "\n".join([
        "",
        "/help",
        "/stop",
        "/clear",
        "/set_language",
        "/set_model",
    ])
    user = users.get(message.from_user.id)
    answer = user.language.value.dictionary.get('help')
    await message.answer(answer + commands)


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

