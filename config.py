import os
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env
load_dotenv()

# Токен для Telegram бота
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# API-ключ OpenAI (ChatGPT)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
