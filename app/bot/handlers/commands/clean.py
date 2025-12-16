import structlog
from aiogram import Router, F
from aiogram.types import Message, ReactionTypeEmoji
from raito import rt
from dishka.integrations.aiogram import FromDishka, inject

from app.bot.utils.roles import ADMINISTRATOR, OWNER, DEVELOPER, USER
from app.services.context import ContextService

logger = structlog.get_logger(__name__)

router = Router(name="commands.clean")


@router.message(
    F.text == ".w clean",
    DEVELOPER | OWNER | ADMINISTRATOR | USER,
)
@rt.description("clean current context")
@inject
async def clean_cmd(
    message: Message,
    context_svc: FromDishka[ContextService],
) -> None:
    if message.chat.type == "private":
        key = str(message.from_user.id)
    elif message.chat.type in ["group", "supergroup"]:
        thread_id = message.message_thread_id if message.is_topic_message else "1"
        key = f"{message.chat.id}:{thread_id}"
        if not await context_svc.is_chat_enabled(key):
            return
    
    await context_svc.clean(key)
    await message.react([ReactionTypeEmoji(emoji="👍")])
