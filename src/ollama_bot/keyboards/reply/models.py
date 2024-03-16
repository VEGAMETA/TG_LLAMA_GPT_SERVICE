from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from project_config import models
from ollama_bot.models.language import Languages
from ollama_bot.keyboards.reply.default import set_cancel_button


def get_model_keyboard(language: Languages = Languages.EN) -> ReplyKeyboardMarkup:
    """
    Returns model keyboard by given language.
    """
    builder = ReplyKeyboardBuilder()
    for model in models:
        builder.button(text=model).adjust(1, True)
    set_cancel_button(builder, language)
    return builder.as_markup()
