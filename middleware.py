from typing import Callable, Awaitable, Dict, Any
from fastapi import BackgroundTasks
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import TelegramObject


class BackgroundMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        # FastAPI кладёт объект в data под ключом background_tasks
        background_tasks: BackgroundTasks = data.get("background_tasks")  # может отсутствовать
        if background_tasks:
            data["background_tasks"] = background_tasks
        return await handler(event, data)
