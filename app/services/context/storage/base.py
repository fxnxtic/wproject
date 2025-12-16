from collections import defaultdict

from tiktoken import encoding_for_model

from app.core.settings import Settings
from app.services.context.storage.protocol import IContextStorage
from app.services.summary import SummaryService
from app.types.context import CONTEXT_ROLE, ConversationContext
from app.utils.key_builder import KeyBuilder as kb
from app.utils.encode import encode


class BaseContextStorage(IContextStorage):
    def __init__(
        self,
        *,
        config: Settings,
        summary_svc: SummaryService,
    ):
        self.config = config
        self.summary_svc = summary_svc

        try:
            self.encode = encoding_for_model(self.config.COMPLETION_MODEL).encode
        except Exception:
            self.encode = encode
        
        self.storage = defaultdict(dict)

    async def _set_chat_status(self, chat_id: str, status: bool) -> None:
        self.storage[kb.chat_status(chat_id)] = status

    async def enable_chat(self, chat_id):
        await self._set_chat_status(chat_id, True)

    async def disable_chat(self, chat_id: str) -> None:
        await self._set_chat_status(chat_id, False)

    async def is_chat_enabled(self, chat_id: str) -> bool:
        return self.storage.get(kb.chat_status(chat_id), False)

    async def set_summary(self, key: str, summary: str) -> None:
        self.storage[kb.summary(key)] = summary

    async def get_summary(self, key: str) -> str | None:
        return self.storage.get(kb.summary(key))

    async def get_messages(
        self, key: str, with_tokens: bool = False
    ) -> ConversationContext | None:
        messages = self.storage.get(kb.messages(key))
        if messages is None:
            return

        if not with_tokens:
            messages = [{"role": m["role"], "content": m["content"]} for m in messages]

        return messages

    async def clean(self, key: str) -> None:
        self.storage.pop(kb.messages(key), None)
        self.storage.pop(kb.summary(key), None)

    async def add_message(self, key: str, role: CONTEXT_ROLE, content: str) -> None:
        tokens = self.tokenizer.encode(content)
        new_entry = {"role": role, "content": content, "tokens": len(tokens)}
        self.storage[kb.messages(key)].append(new_entry)

        messages = self.storage[kb.messages(key)]

        total_tokens = sum(m["tokens"] for m in messages)

        if total_tokens <= self.max_context_tokens:
            return

        tokens_to_remove = total_tokens - self.cutoff_threshold
        removed = []
        while tokens_to_remove > 0 and messages:
            m = messages.pop(0)
            await self.redis.lpop(f"messages:{object}")
            removed.append(m)
            tokens_to_remove -= m["tokens"]

        if removed and self.config.CONTEXT_SUMMARIZE:
            summary = await self.get_summary(key) or []
            base = [{"role": "system", "content": summary}] if summary else []
            summary = await self.summary_svc.summarize(base + removed)
            await self.set_summary(key, summary)