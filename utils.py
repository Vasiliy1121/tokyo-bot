import re
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def itinerary_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton("✏️ Редактировать день", callback_data="edit_day")],
            [InlineKeyboardButton("📥 Экспорт в PDF",        callback_data="export_pdf")],
            [InlineKeyboardButton("🗑️ Удалить маршрут",      callback_data="delete_route")]
        ]
    )


def edit_day_keyboard(itinerary: str) -> InlineKeyboardMarkup:
    days = sorted({int(x) for x in re.findall(r"День\s+(\d+)", itinerary)})
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(f"📅 День {d}", callback_data=f"edit_specific_day_{d}")]
            for d in days
        ]
    )


def split_message(text: str, max_len: int = 4000) -> list[str]:
    parts = []
    while len(text) > max_len:
        idx = text.rfind('\n', 0, max_len)
        idx = idx if idx != -1 else max_len
        parts.append(text[:idx].strip())
        text = text[idx:].strip()
    parts.append(text)
    return parts
