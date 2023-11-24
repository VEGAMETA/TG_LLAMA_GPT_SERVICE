from aiogram.filters.callback_data import CallbackData


class ModelCallback(CallbackData, prefix="model"):
    model: str
