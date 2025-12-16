import structlog
from aiogram import Router
from aiogram.types import Message, ReactionTypeEmoji
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.utils.deep_linking import decode_payload
from dishka.integrations.aiogram import FromDishka, inject
from raito import rt

from app.services.users import UserService, UserCreate
from app.bot.utils.states import States

logger = structlog.get_logger(__name__)

router = Router(name="commands.start")


@router.message(Command("start"))
@rt.description("signup")
@inject
async def start_cmd(
    message: Message,
    command: CommandObject,
    state: FSMContext,
    user_svc: FromDishka[UserService]
) -> None:
    payload = None
    if command.args:
        payload = decode_payload(command.args)

    if not await user_svc.exists(message.from_user.id): # new user 
        inviter_id = None
        if payload and payload.isdigit():   # if user was invited
            inviter = await user_svc.get(int(payload))
            inviter_id = inviter.id

        await user_svc.create(
            UserCreate(
                id=message.from_user.id,
                inviter_id=inviter_id,
                firstname=message.from_user.first_name,
                locale=message.from_user.language_code
            )
        )

    await message.react([ReactionTypeEmoji(emoji="👍")])
    await state.set_state(States.CONVERSATION)

