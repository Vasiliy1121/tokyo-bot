import os
import json
from aiogram import Bot, Dispatcher, types
from aiogram.client.session.aiohttp import AiohttpSession
from fastapi import FastAPI, Request, BackgroundTasks
import uvicorn
from config import TELEGRAM_TOKEN
from handlers import router


session = AiohttpSession(timeout=120)
bot = Bot(token=TELEGRAM_TOKEN, session=session)
dp = Dispatcher()
dp.include_router(router)

app = FastAPI()

WEBHOOK_URL = os.getenv("RENDER_EXTERNAL_URL")

@app.on_event("startup")
async def on_startup():
    await bot.set_webhook(
        f"{WEBHOOK_URL}/webhook",
        allowed_updates=["message", "callback_query", "edited_message", "inline_query", "my_chat_member"]
    )

@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook()

@app.post("/webhook")
async def webhook(request: Request, background_tasks: BackgroundTasks):
    update_json = await request.json()
    update = types.Update(**update_json)

    # Передача background_tasks в state бота (Aiogram)
    await dp.feed_update(bot, update, background_tasks=background_tasks)
    return {"ok": True}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000)
