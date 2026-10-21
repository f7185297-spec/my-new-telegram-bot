"""FSM holatlari."""
from aiogram.fsm.state import State, StatesGroup


class AddAd(StatesGroup):
    photo = State()
    title = State()
    description = State()
    price = State()
    phone = State()
    receipt = State()


class SearchState(StatesGroup):
    query = State()


class AdminReject(StatesGroup):
    reason = State()