from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from ollama_bot.keyboards.reply.default import set_cancel_button
from ollama_bot.misc.gpt import Models
from ollama_bot.models.language import Languages


def get_model_keyboard(language: Languages = Languages.EN) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    for model in Models:
        builder.button(text=model.name,
                       callback_data=f"model:{model.value}").adjust(1, True)
    set_cancel_button(builder, language)
    return builder.as_markup()
