from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from src.models.language import Languages


def get_language_keyboard(language: Languages = Languages.EN) -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(keyboard=[], row_width=1)
    for _language in Languages:
        button = KeyboardButton(text=_language.value.name, callback_data=f"language:{_language.name}")
        keyboard.keyboard.append([button])
    user_language_dictionary = language.value.dictionary
    cancel = KeyboardButton(text=user_language_dictionary.get("command_cancel"), callback_data="default:cancel")
    keyboard.keyboard.append([cancel])
    return keyboard
