import asyncio
from aiogram import Bot, Dispatcher
from config import TELEGRAM_TOKEN
from handlers import router
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.types import BotCommand


async def main():
    print("🚀 Бот успешно запущен!")

    # Устанавливаем команды меню
    await bot.set_my_commands([
        BotCommand(command="start", description="🗓️ Новый маршрут"),
        BotCommand(command="my_routes", description="📌 Мои маршруты"),
        BotCommand(command="export_pdf", description="📁 Экспорт маршрута в PDF"),
        BotCommand(command="cancel", description="🔄 Отменить действие")
    ])

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
