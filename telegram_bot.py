from aiogram import Bot
from config import TELEGRAM_TOKEN
from aiogram.client.session.aiohttp import AiohttpSession

session = AiohttpSession(timeout=120)
bot = Bot(token=TELEGRAM_TOKEN, session=session)