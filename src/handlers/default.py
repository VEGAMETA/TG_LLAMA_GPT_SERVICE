from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.utils.markdown import hbold

from src.filters.default import DefaultCallback
from src.keyboards.reply.gpt import get_model_keyboard
from src.keyboards.reply.language import get_language_keyboard
from src.keyboards.reply.default import get_default_keyboard
from src.models.gpt import RequestStatus
from src.models.user import User, users

from loader import dp


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    CommandStart handler that sends a greeting message.
    """
    user_id = message.from_user.id
    if user_id in users.keys():
        user = users[user_id]
        user.request_status = RequestStatus.NONE
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


@dp.callback_query(DefaultCallback.filter(F.command == "cancel"))
async def show_keyboard(query: CallbackQuery, callback_data: DefaultCallback):
    print('opa')
    await query.answer("Canceled", reply_markup=get_default_keyboard())


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
async def set_model_handler(message: Message) -> None:
    """
    This handler sends models list and allows to set a model.
    """
    user = users.get(message.from_user.id)
    await message.answer(user.language.dictionary.get('set_model'), reply_markup=get_model_keyboard())


@dp.message(Command("set_language"))
async def set_language_handler(message: Message) -> None:
    """
    This handler allows to change the language.
    """
    user = users.get(message.from_user.id)
    await message.answer(user.language.dictionary.get('set_language'), reply_markup=get_language_keyboard())
