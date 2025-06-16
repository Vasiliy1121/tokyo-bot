import openai
import re
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

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

    client = openai.OpenAI()
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

    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=1500
    )

    edited_day_text = response.choices[0].message.content.strip()
    new_itinerary = current_itinerary.replace(day_text, edited_day_text)

    return new_itinerary


import re

def add_google_maps_links(itinerary_text):
    # Функция для создания ссылки
    def make_link(place):
        query = place.strip().replace(' ', '+')
        return f"<a href='https://www.google.com/maps/search/?api=1&query={query}'>{place}</a>"

    # Регулярное выражение, находящее все английские названия мест в тексте
    pattern = re.compile(r"([A-Z][A-Za-z0-9&'\-\s]{2,}(?:Cafe|Museum|Park|Station|City|Road|Bar|Restaurant|Market|Center|Shrine|Temple|Hall|Tower|Broadway|Garden|Ginza|Akihabara|Ikebukuro|Ueno|Nakano|Animate|Mandarake|Taito|Pokémon|Gundam|Sunshine)[A-Za-z0-9&'\-\s]*)")

    # Замена всех найденных названий мест на ссылки
    def replace(match):
        place = match.group(1).strip()
        return make_link(place)

    return pattern.sub(replace, itinerary_text)



