from aiogram.fsm.state import StatesGroup, State

class TripStates(StatesGroup):
    waiting_days = State()               # Ожидание ввода количества дней поездки
    waiting_travelers = State()          # Ожидание ввода состава путешественников
    waiting_interests = State()          # Ожидание ввода интересов
    waiting_pace = State()               # Ожидание выбора темпа путешествия
    waiting_budget = State()             # Ожидание информации о бюджете
    waiting_food = State()               # Ожидание предпочтений по еде
    waiting_special_requests = State()   # Ожидание дополнительных пожеланий
    editing_day = State()                # Редактирование конкретного дня маршрута
