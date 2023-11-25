from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from src.keyboards.reply.default import set_cancel_button
from src.models.language import Languages


def get_language_keyboard(language: Languages = Languages.EN) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    for _language in Languages:
        builder.button(text=_language.value.name, callback_data=f"language:{_language.name}").adjust(1, True)
    set_cancel_button(builder, language)
    return builder.as_markup()
