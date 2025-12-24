import structlog
from aiogram import Router, F
from aiogram.types import Message, ReactionTypeEmoji
from aiogram.fsm.context import FSMContext
from raito import rt
from dishka.integrations.aiogram import FromDishka, inject

from app.bot.utils.roles import ADMINISTRATOR, OWNER, DEVELOPER
from app.bot.utils.states import States
from app.services.context import ContextService

logger = structlog.get_logger(__name__)

router = Router(name="commands.chat_status")


@router.message(
    F.text == ".w enable",
    F.chat.type.in_(["group", "supergroup"]),
    DEVELOPER | OWNER | ADMINISTRATOR,
)
@rt.description("enable bot in chat")
@inject
async def enable_chat_cmd(
    message: Message,
    state: FSMContext,
    context_svc: FromDishka[ContextService],
) -> None:
    await context_svc.enable_chat(message.chat.id)
    await message.react([ReactionTypeEmoji(emoji="👍")])
    await state.set_state(States.CONVERSATION)


@router.message(
    F.text == ".w disable",
    F.chat.type.in_(["group", "supergroup"]),
    DEVELOPER | OWNER | ADMINISTRATOR,
)
@rt.description("disable bot in chat")
@inject
async def disable_chat_cmd(
    message: Message,
    state: FSMContext,
    context_svc: FromDishka[ContextService],
) -> None:
    await context_svc.disable_chat(message.chat.id)
    await message.react([ReactionTypeEmoji(emoji="👍")])
    await state.clear()
