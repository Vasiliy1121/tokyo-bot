
import os
from pathlib import Path

from dotenv import load_dotenv

# .env лежит в корне проекта
ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(ENV_PATH)          # если файла нет – load_dotenv игнорирует

# 1) Telegram‑бот
TELEGRAM_TOKEN: str = os.getenv("TELEGRAM_TOKEN", "")
if not TELEGRAM_TOKEN:
    raise RuntimeError("⛔ TELEGRAM_TOKEN не найден в .env")

# 2) OpenAI API
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
if not OPENAI_API_KEY:
    raise RuntimeError("⛔ OPENAI_API_KEY не найден в .env")

# 3) Google Places API
GOOGLE_PLACES_API_KEY: str = os.getenv("GOOGLE_PLACES_API_KEY", "")
if not GOOGLE_PLACES_API_KEY:
    raise RuntimeError("⛔ GOOGLE_PLACES_API_KEY не найден в .env")

# 4) Хост, на котором запущен сервис (Render, Fly .io, Cloud Run …)
RENDER_EXTERNAL_URL: str = os.getenv("RENDER_EXTERNAL_URL", "")
if not RENDER_EXTERNAL_URL:
    raise RuntimeError("⛔ RENDER_EXTERNAL_URL не найден в .env")

# 5) Полный адрес вебхука
WEBHOOK_PATH: str = "/webhook"
WEBHOOK_URL:  str = f"{RENDER_EXTERNAL_URL.rstrip('/')}{WEBHOOK_PATH}"

# 6) Путь к SQLite‑файлу
DB_PATH: str = os.getenv("DB_PATH", "routes.db")

# Можно вывести в логи (при старте) для проверки:
if __name__ == "__main__":
    print("WEBHOOK_URL =", WEBHOOK_URL)