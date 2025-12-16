from typing import Literal

CONTEXT_ROLE = Literal["system", "user", "assistant"]

type ConversationContext = list[dict[CONTEXT_ROLE, str]]
