import time
import traceback
from typing import Callable, Awaitable, Dict, Any

import structlog
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

__all__ = ["HandleUpdatesMiddleware"]

logger = structlog.get_logger(__name__)


class HandleUpdatesMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user_id = None

        if hasattr(event, "from_user") and event.from_user:
            user_id = event.from_user.id

        handler_name = data["handler"].callback.__name__
        start = time.perf_counter()
        exception = None
        try:
            return await handler(event, data)
        except Exception as e:
            exception = traceback.format_exc()
            raise e
        finally:
            duration = (time.perf_counter() - start) * 1000
            logger.info(
                "New update",
                extra={
                    "user_id": user_id,
                    "chat_id": event.chat.id,
                    "latency": f"{duration:.0f}ms",
                    "event": type(event).__name__,
                    "handler": handler_name,
                }
            )
            if exception:
                logger.error(f"Error in {handler_name}: {exception}")
