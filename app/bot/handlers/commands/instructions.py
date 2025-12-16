import io

from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile
from dishka.integrations.aiogram import FromDishka, inject
from raito import rt, Raito

from app.bot.content import text
from app.services.instructions import InstructionService, InstructionCreate
from app.bot.utils.roles import ADMINISTRATOR, OWNER, DEVELOPER

router = Router(name="commands.instructions")


@router.message(
    F.text == ".w instructions",
    F.chat.type == "private",
    DEVELOPER | OWNER | ADMINISTRATOR,
)
@rt.description("set assistant system prompt")
@inject
async def instructions_cmd(
    message: Message,
    raito: Raito,
    bot: Bot,
    state: FSMContext,
    instruction_svc: FromDishka[InstructionService],
) -> None:
    instructions = await instruction_svc.get_last_prompt()
    if instructions is None:
        await message.answer(text.instructions_empty_cmd)
    else:
        file = BufferedInputFile(instructions.encode("utf-8"), filename="instructions.txt")
        await message.answer_document(
            text=text.instructions_cmd,
            document=file,
        )

    instructions_waiter = await raito.wait_for(state, F.document)
    document = instructions_waiter.message.document
    if document.file_name.endswith(".txt"):
        buffer = io.BytesIO()
        await bot.download(document, buffer)
        prompt = buffer.read().decode()
        await instruction_svc.create(InstructionCreate(
            author_id=instructions_waiter.message.from_user.id,
            prompt=prompt,
        ))
        await instructions_waiter.message.answer(text=text.instructions_updated)
