import json

from redis.asyncio import Redis
from tiktoken import encoding_for_model

from app.core.settings import Settings
from app.enums.context import ContextRole
from app.services.context.storage import IContextStorage
from app.services.summary import SummaryService
from app.utils.key_builder import KeyBuilder as kb
from app.utils.encode import encode
from app.utils.format import as_block


class RedisContextStorage(IContextStorage):
    def __init__(
        self,
        *,
        config: Settings,
        redis: Redis,
        summary_svc: SummaryService,
    ):
        self.config = config
        self.redis = redis
        self.summary_svc = summary_svc

        try:
            self.encode = encoding_for_model(self.config.COMPLETION_MODEL).encode
        except Exception:
            self.encode = encode

    async def enable_chat(self, chat_id):
        await self.redis.set(kb.chat_status(chat_id), 1)

    async def disable_chat(self, chat_id):
        await self.redis.set(kb.chat_status(chat_id), 0)

    async def is_chat_enabled(self, chat_id):
        return bool((await self.redis.get(kb.chat_status(chat_id))))

    async def set_summary(self, key, summary):
        return await self.redis.set(kb.summary(key), summary)

    async def get_summary(self, key):
        return await self.redis.get(kb.summary(key))

    async def get_messages(self, key, with_tokens = False):
        messages = await self.redis.lrange(kb.messages(key), 0, -1)
        messages = [json.loads(m) for m in messages]
        if not with_tokens:
            messages = [{"role": m["role"], "content": m["content"]} for m in messages]
        return messages

    async def clear(self, key):
        await self.redis.delete(kb.messages(key))
        await self.redis.delete(kb.summary(key))

    async def add_message(self, key, role, content):
        tokens = sum(self.encode(content))
        message = json.dumps({"role": role, "content": as_block(content), "tokens": tokens})
        await self.redis.rpush(kb.messages(key), message)

        messages_raw = await self.redis.lrange(kb.messages(key), 0, -1)
        messages = [json.loads(m) for m in messages_raw]

        total_tokens = sum(m["tokens"] for m in messages)

        if total_tokens <= self.config.CONTEXT_MAX_TOKENS:
            return

        tokens_to_remove = total_tokens - self.config.CONTEXT_CUTOFF_THRESHOLD
        removed = []
        while tokens_to_remove > 0 and messages:
            m = messages.pop(0)
            await self.redis.lpop(kb.messages(key))
            removed.append(m)
            tokens_to_remove -= m["tokens"]

        if removed and self.config.CONTEXT_SUMMARIZE:
            summary = await self.get_summary(key) or []
            base = [{"role": ContextRole.SYSTEM, "content": as_block(summary)}] if summary else []
            summary = await self.summary_svc.summarize(base + removed)
            await self.set_summary(key, summary)

    async def get_context(self, key):
        summary = await self.get_summary(key)
        messages = await self.get_messages(key)
        base = [{"role": ContextRole.SYSTEM, "content": as_block(summary)}] if summary else []
        return base + messages
