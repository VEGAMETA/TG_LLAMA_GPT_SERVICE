from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def get_model_keyboard() -> InlineKeyboardMarkup:
    models = ["Model 1", "Model 2", "Model 3", "Cancel"]
    keyboard = InlineKeyboardMarkup(row_width=1)
    for model in models:
        button = InlineKeyboardButton(model, callback_data=f"set_model:{model}")
        keyboard.insert(button)
    return keyboard