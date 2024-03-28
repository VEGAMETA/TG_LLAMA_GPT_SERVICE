from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from ollama_bot.keyboards.reply.default import set_cancel_button
from ollama_bot.misc.language import Languages


def get_subscription_keyboard(language: Languages = Languages.EN) -> ReplyKeyboardMarkup:
    """
    Returns subscription keyboard by given language.
    """
    builder = ReplyKeyboardBuilder()
    for command_name, command in language.items():
        if command_name.startswith("subscription_"):
            builder.button(text=command).adjust(1, True)
    set_cancel_button(builder, language)
    return builder.as_markup()
