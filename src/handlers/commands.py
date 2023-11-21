from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.utils.markdown import hbold
from src.keyboards.inline.models import get_model_keyboard
from src.keyboards.inline.languages import get_language_keyboard
from src.gpt.status import RequestStatus
from src.models.user import create_user, users
from loader import dp


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This is a `/start` command handler that sends a greeting message.
    """
    user_id = message.from_user.id
    if user_id in users.keys():
        users[user_id].request_status = RequestStatus.NONE
        await message.answer(f"Hello again!\nType /help for info")
        return
    create_user(user_id)
    user_name = message.from_user.full_name
    await message.answer(f"""Hello, {hbold(user_name)}
I am gpt bot based on open-source models!
Feel free to ask any question.
type {hbold('/help')} for info
    """)


@dp.message(Command("help"))
async def help_handler(message: Message) -> None:
    commands = """
    /help
    /stop
    /clear
    /set_language
    /set_model
    """
    await message.answer(f"list of commands {commands}")


@dp.message(Command("stop"))
async def stop_handler(message: Message) -> None:
    users.get(message.from_user.id).request_status = RequestStatus.STOP_REQUEST


@dp.message(Command("clear"))
async def clear_handler(message: Message) -> None:
    users.get(message.from_user.id).context.clear()


@dp.message(Command("set_model"))
async def set_model_handler(message: Message) -> None:
    """
    This is a `/set_model` command handler that sends models list and allows to set a model.
    """

    await message.answer("Please select a model:", reply_markup=get_model_keyboard())


@dp.message(Command("set_language"))
async def set_language_handler(message: Message) -> None:
    """
    This is a `/set_language` command handler that allows to change the language.
    """
    await message.answer("Please select a language:", reply_markup=get_language_keyboard())
