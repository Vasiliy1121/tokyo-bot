import re
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Клавиатура после генерации маршрута (кнопка для редактирования дня)
def itinerary_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Редактировать день", callback_data="edit_day")],
        [InlineKeyboardButton(text="📥 Экспорт в PDF", callback_data="export_pdf")],
        [InlineKeyboardButton(text="🗑️ Удалить маршрут", callback_data="delete_route")]
    ])
    return keyboard
# Клавиатура выбора дня для редактирования (генерируется динамически по количеству дней)
def edit_day_keyboard(itinerary):
    days = re.findall(r'День\s+(\d+)', itinerary)
    unique_days = sorted(set(int(day) for day in days))

    buttons = [
        [InlineKeyboardButton(text=f"📅 День {day}", callback_data=f"edit_specific_day_{day}")]
        for day in unique_days
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Функция для разбиения длинного сообщения на части
def split_message(text, max_length=4000):
    messages = []
    while len(text) > max_length:
        split_index = text.rfind('\n', 0, max_length)
        if split_index == -1:
            split_index = max_length
        messages.append(text[:split_index].strip())
        text = text[split_index:].strip()
    messages.append(text)
    return messages
