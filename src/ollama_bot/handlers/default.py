from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.utils.markdown import hbold

from loader import dp
from ollama_bot.keyboards.reply.gpt import get_model_keyboard
from ollama_bot.keyboards.reply.language import get_language_keyboard
from ollama_bot.keyboards.reply.default import get_default_keyboard
from ollama_bot.misc.gpt import RequestStatus
from ollama_bot.models.language import Languages
from ollama_bot.models.user import User, users
from ollama_bot.states.user import UserState


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
        await message.answer(user.language.dictionary.get('restart'), reply_markup=get_default_keyboard())
        return
    user = User.create_user(user_id)
    user_name = message.from_user.full_name
    await message.answer(
        user.language.dictionary.get('greeting') +
        hbold(user_name) +
        user.language.dictionary.get('start'),
        reply_markup=get_default_keyboard()
    )


languages = [language.value.dictionary.get("cancel").casefold() for language in Languages if
             language.value.dictionary.get("cancel")]


@dp.message(Command("cancel"))
@dp.message(F.text.casefold().in_(languages))
async def cancel_handler(message: Message, state: FSMContext) -> None:
    """
    Allows user to cancel any action
    """
    current_state = await state.get_state()
    if current_state == UserState.chatting:
        return

    await state.set_state(UserState.chatting)
    await message.answer("Cancelled.", reply_markup=get_default_keyboard())


@dp.message(Command("help"))
async def help_handler(message: Message) -> None:
    """
    Help command handler sends list of commands
    """
    commands: str = "\n".join([
        "/help",
        "/stop",
        "/clear",
        "/set_language",
        "/set_model",
    ])
    user = users.get(message.from_user.id)
    await message.answer(user.language.dictionary.get('help') + commands)


@dp.message(Command("stop"))
async def stop_handler(message: Message) -> None:
    """
    Request for gpt to stop answering
    """
    user = users.get(message.from_user.id)
    user.request_status = RequestStatus.STOP_REQUEST


@dp.message(Command("clear"))
async def clear_handler(message: Message) -> None:
    """
    Clears the context for user gpt request
    """
    user = users.get(message.from_user.id)
    user.context.clear()
    await message.answer(user.language.dictionary.get('context'))


@dp.message(Command("set_model"))
async def set_model_handler(message: Message, state: FSMContext) -> None:
    """
    This handler sends models list and allows to set a model.
    """
    await state.set_state(UserState.choosing_model)
    user = users.get(message.from_user.id)
    await message.answer(user.language.dictionary.get('set_model'), reply_markup=get_model_keyboard())


@dp.message(Command("set_language"))
async def set_language_handler(message: Message, state: FSMContext) -> None:
    """
    This handler allows to change the language.
    """
    await state.set_state(UserState.choosing_language)
    user = users.get(message.from_user.id)
    await message.answer(user.language.dictionary.get('set_language'), reply_markup=get_language_keyboard())
