from aiogram import F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from loader import dp
from ollama_bot.models.user import User
from ollama_bot.states.user import UserState
from ollama_bot.misc.commands import commands
from ollama_bot.models.language import Languages
from ollama_bot.keyboards.reply.default import get_default_keyboard
from ollama_bot.keyboards.reply.language import get_language_keyboard


@dp.message(Command("set_language"))
@dp.message(F.text.in_(commands.get("command_set_language")))
async def set_language_handler(message: Message, state: FSMContext) -> None:
    """
    This handler allows to change the language.
    """
    await state.set_state(UserState.choosing_language)
    user = await User.get_user_by_id(message.from_user.id)
    language = await Languages.get_dict_by_name(user.language)
    answer = language.get('set_language')
    await message.answer(answer, reply_markup=get_language_keyboard(language))


@dp.message(UserState.choosing_language)
async def langugage_change_handler(message: Message, state: FSMContext) -> None:
    """
    Allows user to cancel any action
    """
    await state.set_state(UserState.chatting)
    user_id = message.from_user.id
    user = await User.get_user_by_id(user_id)
    user_language = await Languages.get_dict_by_name(user.language)
    for language in Languages:
        if message.text == language.value.name:
            await User.set_language(user_id, language)
            answer = language.value.dictionary.get('set_language_after')
            await message.answer(answer, reply_markup=get_default_keyboard(language.value.dictionary))
            return
    else:
        answer = user_language.get('error')
        await message.answer(answer, reply_markup=get_default_keyboard(user_language))
