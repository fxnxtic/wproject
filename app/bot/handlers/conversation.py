import structlog
from aiogram import F, Router, Bot
from aiogram.types import Message
from aiogram.filters import StateFilter
from aiogram.utils.chat_action import ChatActionSender
from dishka.integrations.aiogram import FromDishka, inject

from app.bot.utils.roles import ADMINISTRATOR, DEVELOPER, OWNER, USER
from app.bot.utils.states import States
from app.enums.context import ContextRole
from app.services.completion import CompletionService
from app.services.context import ContextService
from app.services.users import User, UserService
from app.utils.key_builder import KeyBuilder as kb

_USERNAME: str | None = None

logger = structlog.get_logger(__name__)

router = Router(name="conversation")


def _prepare_user_message(message: Message, user: User) -> str:
    answered_to = (
        f"<answer to msg {message.reply_to_message.message_id}>"
        if message.reply_to_message
        else ""
    )
    user_info = "<role={}, name={}, tag={}, msg_id={}>".format(
        user.role, user.firstname, message.from_user.username, message.message_id
    )
    return user_info + " " + answered_to + "\n" + message.text


def _prepare_assistant_message(message: Message) -> str:
    return f"<msg_id={message.message_id}>\n" + message.text


@router.message(
    F.text,
    DEVELOPER | OWNER | ADMINISTRATOR | USER,
    StateFilter(States.CONVERSATION),
)
@inject
async def on_message(
    message: Message,
    bot: Bot,
    context_svc: FromDishka[ContextService],
    completion_svc: FromDishka[CompletionService],
    user_svc: FromDishka[UserService],
) -> None:
    if message.text.startswith(("/", ".w")):
        return

    if message.chat.type == "private":
        key = kb.user_obj(message.from_user.id)
    elif message.chat.type in ["group", "supergroup"]:
        thread_id = message.message_thread_id if message.is_topic_message else "1"
        key = kb.group_obj(message.chat.id, thread_id)
        if not await context_svc.is_chat_enabled(message.chat.id, thread_id):
            logger.debug("Chat not enabled")
            return

        global _USERNAME
        if _USERNAME is None:
            _USERNAME = (await bot.get_me()).username

        if ("@" + _USERNAME) not in message.text:
            logger.debug("Message have not tag")
            return
    else:
        logger.debug("Invalid chat type")
        return

    user = await user_svc.get(message.from_user.id)
    if user is None:
        logger.debug("User not found")
        return

    await context_svc.add_message(
        key=key,
        role=ContextRole.USER,
        content=_prepare_user_message(message, user),
    )

    context = await context_svc.get_context(key)
    if context is None:
        logger.debug("context not found")
        return

    async with ChatActionSender(
        bot=bot,
        chat_id=message.chat.id,
        message_thread_id=message.message_thread_id
        if message.is_topic_message
        else None,
        action="typing",
    ):
        completion = await completion_svc.complete(
            context=context,
            user_id=message.from_user.id,
            chat_id=message.chat.id,
        )

        response = await message.answer(completion)
        await context_svc.add_message(
            key=key,
            role=ContextRole.ASSISTANT,
            content=_prepare_assistant_message(response),
        )
