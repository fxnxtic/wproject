from sqlalchemy import select

from app.database import Database, SQLAlchemyRepository
from app.services.instructions.model import InstructionModel
from app.services.instructions.schemas import InstructionCreate, InstructionUpdate


class InstructionRepository(SQLAlchemyRepository[InstructionModel, InstructionCreate, InstructionUpdate]):
    def __init__(self, db: Database):
        super().__init__(InstructionModel, db)

    async def get_last_prompt(self) -> str | None:
        async with self.db.get_session() as session:
            stmt = select(InstructionModel.prompt).order_by(InstructionModel.created_at.desc()).limit(1)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()