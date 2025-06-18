import os
from aiogram import Bot, Dispatcher, types
from aiogram.client.session.aiohttp import AiohttpSession
from fastapi import FastAPI
import uvicorn
from config import TELEGRAM_TOKEN
from handlers import router
import json

# Настройки бота
session = AiohttpSession(timeout=120)
bot = Bot(token=TELEGRAM_TOKEN, session=session)
dp = Dispatcher()
dp.include_router(router)

# FastAPI приложение
app = FastAPI()

WEBHOOK_URL = os.getenv("RENDER_EXTERNAL_URL")

@app.on_event("startup")
async def on_startup():
    await bot.set_webhook(f"{WEBHOOK_URL}/webhook")

@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook()

@app.post("/webhook")
async def webhook(update: dict):
    telegram_update = types.Update(**update)
    print("🔵 Получен запрос от Telegram:", json.dumps(update, indent=4, ensure_ascii=False))
    await dp.feed_update(bot, telegram_update)
    return {"ok": True}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000)
