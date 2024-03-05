from aiogram.fsm.state import StatesGroup, State


class UserState(StatesGroup):
    chatting = State()
    choosing_model = State()
    choosing_language = State()
