import os
from fastapi import FastAPI, Request, BackgroundTasks
from aiogram import types
from bot_init import bot, dp

app = FastAPI()

@app.on_event("startup")
async def on_startup():
    await bot.set_webhook(f"{os.getenv('RENDER_EXTERNAL_URL')}/webhook")

@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook()

@app.post("/webhook")
async def webhook(request: Request, background_tasks: BackgroundTasks):
    update_json = await request.json()
    update = types.Update(**update_json)
    await dp.feed_update(bot, update, background_tasks=background_tasks)
    return {"ok": True}