from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_language_keyboard() -> InlineKeyboardMarkup:
    languages = ["English", "Interslavic", "Russian", "Cancel"]
    keyboard = InlineKeyboardMarkup(row_width=1)
    for language in languages:
        button = InlineKeyboardButton(language, callback_data=f"set_language:{language}")
        keyboard.insert(button)
    return keyboard
