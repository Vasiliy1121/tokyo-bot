import requests
import os
from dotenv import load_dotenv


load_dotenv()

GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")

def get_place_details(place_name):
    url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
    params = {
        "input": place_name,
        "inputtype": "textquery",
        "fields": "name,formatted_address,geometry,rating,opening_hours,place_id",
        "key": GOOGLE_PLACES_API_KEY,
        "language": "ru"
    }

    response = requests.get(url, params=params)
    result = response.json()

    if result["status"] == "OK" and result["candidates"]:
        return result["candidates"][0]
    else:
        return None


if __name__ == "__main__":
    place_name = "Ueno Park Tokyo"
    place = get_place_details(place_name)

    if place:
        print("✅ Место найдено!")
        print(f"Название: {place['name']}")
        print(f"Адрес: {place['formatted_address']}")
        print(f"Рейтинг: {place.get('rating', 'Нет рейтинга')}")

        opening_hours = place.get('opening_hours', {}).get('weekday_text')
        if opening_hours:
            print("🕒 Часы работы:")
            for day in opening_hours:
                print(f" - {day}")
        else:
            print("🕒 Часы работы: Нет данных")
    else:
        print("❌ Место не найдено!")