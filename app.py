from fastapi import FastAPI, Request, BackgroundTasks
from aiogram import types
from bot_init import bot, dp
from config  import WEBHOOK_PATH, WEBHOOK_URL
from db      import init_db

app = FastAPI()

@app.on_event("startup")
async def startup():
    init_db()
    await bot.set_webhook(WEBHOOK_URL)

@app.on_event("shutdown")
async def shutdown():
    await bot.delete_webhook()

@app.post(WEBHOOK_PATH)
async def telegram_webhook(req: Request, background_tasks: BackgroundTasks):
    update = types.Update(**await req.json())
    await dp.feed_update(bot, update, background_tasks=background_tasks)
    return {"ok": True}

@app.get("/")       # чтобы убрать 404 в логах
async def root():
    return {"status": "ok"}
