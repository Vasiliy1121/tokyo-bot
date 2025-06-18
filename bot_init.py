from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.storage.memory import MemoryStorage
from config import TELEGRAM_TOKEN
from handlers import router

session = AiohttpSession(timeout=120)
bot = Bot(token=TELEGRAM_TOKEN, session=session)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
dp.include_router(router)