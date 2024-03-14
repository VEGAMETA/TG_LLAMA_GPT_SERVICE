from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from ollama_bot.models.language import Languages


def get_default_keyboard(language: Languages = Languages.EN) -> ReplyKeyboardMarkup:
    """
    Returns default keyboard by given language.
    """
    builder = ReplyKeyboardBuilder()
    for command_name, command in language.items():
        if command_name.startswith("command_"):
            builder.button(text=command).adjust(1, True)
    return builder.as_markup()


def set_cancel_button(builder: ReplyKeyboardBuilder, language: Languages):
    """
    Sets cancel button by given language.
    """
    text = language.get("cancel")
    builder.button(text=text).adjust(1, True)
