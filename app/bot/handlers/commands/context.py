import structlog
from aiogram import Router, F
from aiogram.types import Message, BufferedInputFile
from raito import rt
from dishka.integrations.aiogram import FromDishka, inject

from app.bot.utils.roles import DEVELOPER
from app.services.context import ContextService
from app.bot.content import text

logger = structlog.get_logger(__name__)

router = Router(name="commands.context")


@router.message(F.text == ".w context", DEVELOPER)
@rt.description("print current context")
@inject
async def context_cmd(message: Message, context_svc: FromDishka[ContextService]) -> None:
    if message.chat.type == "private":
        key = str(message.from_user.id)
    elif message.chat.type in ["group", "supergroup"]:
        thread_id = message.message_thread_id if message.is_topic_message else "1"
        key = f"{message.chat.id}:{thread_id}"

    context = await context_svc.get_context(key)
    if context is None:
        await message.answer(text=text.context_empty_cmd)
    else:
        conversation = "/n".join([f"{ctx['role']}: {ctx['content']}" for ctx in context])
        file = BufferedInputFile(conversation.encode(encoding="utf-8"), filename="context.txt")
        await message.answer_document(document=file, text=text.context_cmd)
