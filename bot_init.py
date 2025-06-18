from aiogram import Bot, Dispatcher
from config import TELEGRAM_TOKEN
from middleware import BackgroundTasksMiddleware
from handlers import router

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

dp.include_router(router)
dp.message.middleware(BackgroundTasksMiddleware())
dp.callback_query.middleware(BackgroundTasksMiddleware())