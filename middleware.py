from aiogram.dispatcher.middlewares.base import BaseMiddleware
from fastapi import BackgroundTasks

class BackgroundTasksMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        background_tasks: BackgroundTasks = data['background_tasks']
        data["background_tasks"] = background_tasks
        return await handler(event, data)