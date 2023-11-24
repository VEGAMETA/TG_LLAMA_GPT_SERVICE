from aiogram.filters.callback_data import CallbackData


class DefaultCallback(CallbackData, prefix="default"):
    command: str
