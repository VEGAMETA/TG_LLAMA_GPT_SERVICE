from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from src.models.language import Languages


def get_default_keyboard(language: Languages = Languages.EN):
    user_language_dictionary = language.value.dictionary
    commands = {
        user_language_dictionary.get("command_help"): "default:help",
        user_language_dictionary.get("command_stop"): "default:stop",
        user_language_dictionary.get("command_clear"): "default:clear",
        user_language_dictionary.get("command_set_language"): "default:set_language",
        user_language_dictionary.get("command_set_model"): "default:set_model",
    }
    keyboard = ReplyKeyboardMarkup(keyboard=[], row_width=1)
    for text, command in commands.items():
        button = KeyboardButton(text=text, callback_data=command)
        keyboard.keyboard.append([button])
    return keyboard
