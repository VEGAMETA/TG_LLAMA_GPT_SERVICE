from aiogram import F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from loader import dp
from ollama_bot.misc.gpt import Models
from ollama_bot.models.language import Languages
from ollama_bot.models.user import User
from ollama_bot.states.user import UserState
from ollama_bot.misc.commands import commands
from ollama_bot.keyboards.reply.models import get_model_keyboard
from ollama_bot.keyboards.reply.default import get_default_keyboard


@dp.message(Command("set_model"))
@dp.message(F.text.in_(commands.get("command_set_model")))
async def set_model_handler(message: Message, state: FSMContext) -> None:
    """
    This handler sends models list and allows to set a model.
    """
    await state.set_state(UserState.choosing_model)
    user = await User.get_user_by_id(message.from_user.id)
    language = await Languages.get_dict_by_name(user.language)
    answer = language.get('set_model')
    await message.answer(answer, reply_markup=get_model_keyboard(language))


@dp.message(UserState.choosing_model)
async def model_change_handler(message: Message, state: FSMContext) -> None:
    """
    Changes model from list
    """
    await state.set_state(UserState.chatting)
    user_id = message.from_user.id
    user = await User.get_user_by_id(user_id)
    language = await Languages.get_dict_by_name(user.language)
    for model in Models:
        if message.text == model.name:
            await User.set_model(user_id, model)
            answer = language.get('set_model_after') + model.name
            await message.answer(answer, reply_markup=get_default_keyboard(language))
            return
    else:
        answer = language.get('error')
        await message.answer(answer, reply_markup=get_default_keyboard(language))
