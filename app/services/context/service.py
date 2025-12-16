import structlog

from app.types.context import CONTEXT_ROLE, ConversationContext

from .storage.base import IContextStorage

logger = structlog.get_logger(__name__)


class ContextService:
    def __init__(self, storage: IContextStorage) -> None:
        self.storage = storage

    async def startup(self) -> None:
        logger.info("Context service started")

    async def shutdown(self) -> None:
        logger.info("Context service stopped")

    async def enable_chat(self, chat_id: str) -> None:
        await self.storage.enable_chat(chat_id)

    async def disable_chat(self, chat_id: str) -> None:
        await self.storage.disable_chat(chat_id)

    async def is_chat_enabled(self, chat_id: str) -> bool:
        return await self.storage.is_chat_enabled(chat_id)

    async def get_summary(self, key: str) -> str | None:
        return await self.storage.get_summary(key)
    
    async def set_summary(self, key: str, summary: str) -> None:
        await self.storage.set_summary(key, summary)

    async def add_message(self, key: str, role: CONTEXT_ROLE, content: str) -> None:
        await self.storage.add_message(key, role, content)

    async def clean(self, key: str) -> None:
        await self.storage.clean(key)

    async def get_context(self, key: str) -> ConversationContext | None:
        return await self.storage.get_context(key)
