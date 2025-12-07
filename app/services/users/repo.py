from sqlalchemy import select, update

from app.database import Database, SQLAlchemyRepository
from app.services.users.model import UserModel
from app.services.users.schemas import UserCreate, UserUpdate


class UserRepository(SQLAlchemyRepository[UserModel, UserCreate, UserUpdate]):
    def __init__(self, db: Database):
        super().__init__(UserModel, db)

    async def get_role(self, id: int) -> str | None:
        async with self.db.get_session() as session:
            stmt = select(UserModel.role).where(UserModel.id == id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        
    async def set_role(self, id: int, role: str) -> None:
        async with self.db.get_session() as session:
            stmt = update(UserModel).where(UserModel.id == id).values(role=role)
            await session.execute(stmt)
            await session.flush()
            await session.refresh(UserModel)

    async def remove_role(self, id: int) -> None:
        async with self.db.get_session() as session:
            stmt = update(UserModel).where(UserModel.id == id).values(role=None)
            await session.execute(stmt)
            await session.flush()
            await session.refresh(UserModel)

    async def get_user_ids_with_role(self, role: str) -> list[int]:
        async with self.db.get_session() as session:
            stmt = select(UserModel.id).where(UserModel.role == role)
            result = await session.execute(stmt)
            return result.scalars().all()
