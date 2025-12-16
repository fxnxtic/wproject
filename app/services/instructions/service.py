import structlog

from app.database import Database, SQLAlchemyService
from app.services.instructions.model import InstructionModel
from app.services.instructions.repo import InstructionRepository
from app.services.instructions.schemas import Instruction, InstructionCreate, InstructionUpdate

logger = structlog.get_logger(__name__)


class InstructionService(SQLAlchemyService[InstructionModel, InstructionCreate, InstructionUpdate, Instruction]):
    def __init__(self, db: Database):
        repo = InstructionRepository(db)
        super().__init__(repo, Instruction)

    async def startup(self):
        logger.info("Instruction service started")

    async def shutdown(self):
        logger.info("Instruction service stopped")

    async def get_last_prompt(self) -> str | None:
        return await self.repo.get_last_prompt()
