from aiogram import Bot, Dispatcher
from config import TELEGRAM_TOKEN
from middleware import BackgroundMiddleware
from handlers import router  # импорт после создания Bot не нужен – циклов нет

bot = Bot(token=TELEGRAM_TOKEN, parse_mode="Markdown")
dp  = Dispatcher()
dp.message.middleware(BackgroundMiddleware())
dp.callback_query.middleware(BackgroundMiddleware())
dp.include_router(router)
