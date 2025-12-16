import structlog
from openrouter import OpenRouter

from app.core.settings import Settings
from app.enums.context import ContextRole
from app.types.context import ConversationContext
from app.utils.format import as_block

logger = structlog.get_logger(__name__)

SUMMARIZE_SYSTEM_PROMPT = """You are a helpful assistant that summarizes conversations."""
SUMMARIZE_USER_PROMPT = """Summarize the following conversation, using the same language:\n"""


class SummaryService:
    def __init__(self, config: Settings) -> None:
        self.config = config

    async def startup(self):
        logger.info("Summary service started")

    async def shutdown(self):
        logger.info("Summary service stopped")

    async def summarize(self, context: ConversationContext) -> str:
        async with OpenRouter(
            api_key=self.config.OPENROUTER_API_KEY,
            server_url=self.config.OPENROUTER_API_URL,
        ) as router:
            base = [{"role": ContextRole.SYSTEM, "content": as_block(SUMMARIZE_SYSTEM_PROMPT)}]
            conversation = "/n".join([f"{ctx['role']}: {ctx['content']}" for ctx in context])
            messages = [{"role": ContextRole.USER, "content": as_block(SUMMARIZE_USER_PROMPT + conversation)}]

            summary = await router.completions.generate_async(
                model=self.config.SUMMARY_MODEL,
                prompt=base + messages,
                max_tokens=self.config.SUMMARY_MAX_TOKENS,
            )
            return summary.choices[0].message.content
