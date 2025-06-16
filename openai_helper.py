from openai import OpenAI
import re
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def generate_itinerary(data):
    prompt = f"""
    Ты — эксперт по туризму и профессиональный гид в Японии, специализирующийся на создании маршрутов по Токио.

    Пользователь запросил маршрут:

    1. Длительность: {data['days']} дней.
    2. Состав: {data['travelers']}.
    3. Интересы: {data['interests']}.
    4. Темп: {data['pace']}.
    5. Бюджет: {data['budget']}.
    6. Предпочтения в еде: {data['food']}.
    7. Особые пожелания: {data['special_requests']}.

    Составь подробный маршрут по дням (Утро, День, Вечер). Названия мест на английском, текст на русском.
    """

    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=3000
    )

    itinerary = response.choices[0].message.content.strip()
    return add_google_maps_links(itinerary)


async def edit_day(current_itinerary, day_number, user_request):
    day_pattern = rf"(📅?\s*День\s*{day_number}.*?)(?=(📅?\s*День\s*\d+)|\Z)"
    match = re.search(day_pattern, current_itinerary, re.DOTALL)

    if not match:
        raise ValueError(f"Не найден День {day_number}")

    day_text = match.group(1).strip()

    prompt = f"""
    Текущий День {day_number}:

    {day_text}

    Пользователь хочет изменить день так:
    "{user_request}"

    Пересоздай День {day_number}, учтя пожелания, структура (Утро, День, Вечер).
    """

    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=1500
    )

    edited_day_text = response.choices[0].message.content.strip()
    new_itinerary = current_itinerary.replace(day_text, edited_day_text)

    return new_itinerary


def add_google_maps_links(itinerary_text):
    def replace_link(match):
        action, place = match.groups()
        query = place.strip().replace(' ', '+')
        link = f"[{place.strip()}](https://www.google.com/maps/search/?api=1&query={query})"
        return f"- {action} {link}"

    pattern = re.compile(
        r"-\s*(Посетите|Посещение|Экскурсия по|Экскурсия в|Прогулка по|Ужин в|Завтрак в|Обед в|Посетить|Проведите утро в)\s+([^\.,\n]+)"
    )
    return pattern.sub(replace_link, itinerary_text)
