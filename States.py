from aiogram.fsm.state import State, StatesGroup


class UserStates(StatesGroup):
    location = State()
    feedback = State()