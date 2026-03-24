import json
import re
from typing import Any

import structlog
from openrouter import OpenRouter

from app.core.settings import Settings
from app.enums.context import ContextRole
from app.services.execution import ExecutionService
from app.services.instructions import InstructionService
from app.types.context import ConversationContext
from app.utils.format import as_block

logger = structlog.get_logger(__name__)


class CompletionService:
    def __init__(
        self,
        *,
        config: Settings,
        instructions_svc: InstructionService,
        execution_svc: ExecutionService,
    ) -> None:
        self.router = OpenRouter()
        self.config = config
        self.instructions_svc = instructions_svc
        self.execution_svc = execution_svc

    async def startup(self):
        logger.info("Completion service started")

    async def shutdown(self):
        logger.info("Completion service stopped")

    async def _get_system_prompt(self) -> str | None:
        system_prompt = await self.instructions_svc.get_last_prompt()
        # if system_prompt is None:
        #    raise ValueError("System prompt not found")

        return system_prompt

    async def complete(
        self, context: ConversationContext, user_id: str, chat_id: str
    ) -> list[dict[str, Any]]:
        if user_id is not None:
            logger.bind(user_id=user_id)
        if chat_id is not None:
            logger.bind(chat_id=chat_id)

        instructions = await self._get_system_prompt()

        prompt = (
            [{"role": ContextRole.SYSTEM, "content": as_block(instructions)}] + context
            if instructions
            else context
        )
        req = context[-1]["content"][0]["text"].split("\n", 2)[1]
        logger.debug(f"Requests <{(req[:97] + '...') if len(req) > 100 else req}>")

        answers: list[dict[str, Any]] = []

        async with OpenRouter(
            api_key=self.config.OPENROUTER_API_KEY,
            server_url=self.config.OPENROUTER_API_URL,
        ) as router:
            while True:
                comp = await router.chat.send_async(
                    messages=prompt + answers,
                    model=self.config.COMPLETION_MODEL,
                    max_tokens=self.config.COMPLETION_MAX_TOKENS,
                    temperature=self.config.COMPLETION_TEMPERATURE,
                    tools=self.execution_svc.resolve_all(),
                )

                msg = comp.choices[0].message

                # --- 1. если есть tool calls ---
                if getattr(msg, "tool_calls", None):
                    prompt.append(
                        {
                            "role": ContextRole.ASSISTANT,
                            "content": msg.content,
                        }
                    )

                    for tool_call in msg.tool_calls:
                        tool_name = tool_call.function.name
                        args = json.loads(tool_call.function.arguments)

                        result = await self.execution_svc.use_tool(tool_name, **args)

                        answers.append(
                            {
                                "role": ContextRole.TOOL,
                                "tool_call_id": tool_call.id,
                                "content": result,
                            }
                        )

                    continue

                response = str(comp.choices[0].message.content)
                if response.startswith(""):
                    response = re.sub(r"^<[^>]+>\s*", "", response, 1)

                answers.append({"role": ContextRole.ASSISTANT, "content": response})

                logger.debug(
                    f"Response <{(response[:97] + '...') if len(response) > 100 else response}>"
                )
                logger.debug(
                    f"Tokens usage <input: {comp.usage.prompt_tokens}, output: {comp.usage.completion_tokens}, total: {comp.usage.total_tokens}>"
                )

                return answers
