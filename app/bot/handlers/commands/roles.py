from aiogram import Router, Bot, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from raito import Raito
from raito.handlers.roles.assign import show_roles
from raito.handlers.roles.revoke import revoke
from raito.handlers.roles.staff import list_staff

from app.bot.utils.roles import ADMINISTRATOR, OWNER, DEVELOPER

router = Router(name="commands.roles")


@router.message(F.text == ".w assign", ADMINISTRATOR | OWNER | DEVELOPER)
async def assign_role_cmd(message: Message, raito: Raito, state: FSMContext):
    await state.clear()
    await show_roles(message, raito)

@router.message(F.text == ".w revoke", ADMINISTRATOR | OWNER | DEVELOPER)
async def revoke_role_cmd(message: Message, state: FSMContext):
    await state.clear()
    await revoke(message, state)

@router.message(F.text == ".w staff", ADMINISTRATOR | OWNER | DEVELOPER)
async def staff_cmd(message: Message, state: FSMContext, raito: Raito, bot: Bot):
    await state.clear()
    await list_staff(message, raito, bot)
