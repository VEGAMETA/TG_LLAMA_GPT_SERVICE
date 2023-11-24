from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from src.models.gpt import Models
from src.models.language import Languages


def get_model_keyboard(language: Languages = Languages.EN) -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(keyboard=[], row_width=1)
    for model in Models:
        button = KeyboardButton(text=model.name, callback_data=f"model:{model.value}")
        keyboard.keyboard.append([button])
    user_language_dictionary = language.value.dictionary
    cancel = KeyboardButton(text=user_language_dictionary.get("command_cancel", callback_data="default:cancel"))
    keyboard.keyboard.append([cancel])
    return keyboard
