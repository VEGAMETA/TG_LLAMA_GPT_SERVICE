from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from src.filters.default import DefaultCallback
from src.models.language import Languages


def get_default_keyboard(language: Languages = Languages.EN) -> ReplyKeyboardMarkup:
    user_language_dictionary = language.value.dictionary
    commands = {v: "default:" + k.rstrip("command_") for k, v in user_language_dictionary.items() if
                k.startswith("command_")}
    builder = ReplyKeyboardBuilder()
    for text, command in commands.items():
        builder.button(text=text, callback_data=command).adjust(1, True)
    return builder.as_markup()


def set_cancel_button(builder: ReplyKeyboardBuilder, language: Languages):
    builder.button(
        text=language.value.dictionary.get("cancel"),
        callback_data=DefaultCallback(command="cancel").pack()
    ).adjust(1, True)
