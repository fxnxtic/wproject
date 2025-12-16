import re
import structlog
from openrouter import OpenRouter

from app.core.settings import Settings
from app.enums.context import ContextRole
from app.types.context import ConversationContext
from app.services.instructions import InstructionService
from app.utils.format import as_block

logger = structlog.get_logger(__name__)


class CompletionService:
    def __init__(
        self,
        *,
        config: Settings, 
        instructions_svc: InstructionService
    ) -> None:
        self.router = OpenRouter()
        self.config = config
        self.instructions_svc = instructions_svc

    async def startup(self):
        logger.info("Completion service started")

    async def shutdown(self):
        logger.info("Completion service stopped")

    async def _get_system_prompt(self) -> str:
        system_prompt = await self.instructions_svc.get_last_prompt()
        if system_prompt is None:
            raise ValueError("System prompt not found")

        return system_prompt

    async def complete(
        self, context: ConversationContext, user_id: str, chat_id: str
    ) -> str:
        if user_id is not None:
            logger.bind(user_id=user_id)
        if chat_id is not None:
            logger.bind(chat_id=chat_id)

        prompt = [
            {"role": ContextRole.SYSTEM, "content": as_block(await self._get_system_prompt())}
        ] + context
        req = context[-1]["content"][0]["text"].split("\n", 2)[1]
        logger.debug(f"Requests <{(req[:97] + '...') if len(req) > 100 else req}>")

        logger.debug(prompt)

        async with OpenRouter(
            api_key=self.config.OPENROUTER_API_KEY,
            server_url=self.config.OPENROUTER_API_URL,
        ) as router:
            comp = await router.chat.send_async(
                messages=prompt,
                model=self.config.COMPLETION_MODEL,
                max_tokens=self.config.COMPLETION_MAX_TOKENS,
                temperature=self.config.COMPLETION_TEMPERATURE,
            )
            response = str(comp.choices[0].message.content)
            if response.startswith(""):
                response = re.sub(r"^<[^>]+>\s*", "", response, 1)

        logger.debug(
            f"Response <{(response[:97] + '...') if len(response) > 100 else response}>"
        )
        logger.debug(
            f"Tokens usage <input: {comp.usage.prompt_tokens}, output: {comp.usage.completion_tokens}, total: {comp.usage.total_tokens}>"
        )

        return response
