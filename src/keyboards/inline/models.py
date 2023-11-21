from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from src.gpt.models import Models

def get_model_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=1)
    for model in Models:
        button = InlineKeyboardButton(model.name, callback_data=f"set_model:{model.name}")
        keyboard.insert(button)
    return keyboard