from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from ollama_bot.models.language import Languages
from ollama_bot.keyboards.reply.default import set_cancel_button


def get_language_keyboard(language: Languages = Languages.EN) -> ReplyKeyboardMarkup:
    """
    Returns language keyboard by given language.
    """
    builder = ReplyKeyboardBuilder()
    for _language in Languages:
        builder.button(text=_language.value.name).adjust(1, True)
    set_cancel_button(builder, language)
    return builder.as_markup()
