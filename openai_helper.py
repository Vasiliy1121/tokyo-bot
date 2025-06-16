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


def add_google_maps_links(itinerary_text):
    # Создаём markdown-ссылку
    def make_link(place):
        query = place.strip().replace(' ', '+')
        return f"[{place}](https://www.google.com/maps/search/?api=1&query={query})"

    # Ищем названия в скобках на английском
    pattern_brackets = re.compile(r'([А-Яа-яЁё\s]+)\s*\(([\w\s\'&-]+)\)')

    # Сначала заменяем названия формата "Русское (English)"
    itinerary_text = pattern_brackets.sub(lambda m: f"{m.group(1).strip()} ({make_link(m.group(2).strip())})", itinerary_text)

    # Затем находим и добавляем ссылки на отдельные английские названия без скобок
    english_place_pattern = re.compile(r'\b([A-Z][A-Za-z0-9&\'\-]+\s?(Park|Museum|City|Center|Plaza|Garden|Shrine|Temple|Bridge|Station|Tower|Broadway|Market|Cafe|Restaurant|Hall|Disneyland|DisneySea|Animate|Mandarake|Gundam|Pokémon|Sunshine|Nakano|Asakusa|Akihabara|Ikebukuro|Ueno|Odaiba|Fuji|Miraikan|Sumida|Hibiya|Marunouchi))\b')

    itinerary_text = english_place_pattern.sub(lambda m: make_link(m.group(1)), itinerary_text)

    return itinerary_text



