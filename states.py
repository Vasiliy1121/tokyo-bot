from aiogram.fsm.state import StatesGroup, State


class TripStates(StatesGroup):
    waiting_days            = State()
    waiting_travelers       = State()
    waiting_interests       = State()
    waiting_pace            = State()
    waiting_budget          = State()
    waiting_food            = State()
    waiting_special_requests= State()
    editing_day             = State()
