from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, CommandObject
from aiogram.utils.deep_linking import decode_payload
from dishka.integrations.aiogram import FromDishka, inject

from app.services.users import UserService, UserCreate

router = Router(name="commands")


@router.message(Command("start"))
@inject
async def start(message: Message, command: CommandObject, user_svc: FromDishka[UserService]) -> None:
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
                role=None,  # default user have not role
                inviter_id=inviter_id,
                firstname=message.from_user.first_name,
                locale=message.from_user.language_code
            )
        )

    await message.answer("Hello!")
