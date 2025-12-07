import structlog

from app.database import Database, SQLAlchemyService
from app.services.users.model import UserModel
from app.services.users.repo import UserRepository
from app.services.users.schemas import User, UserCreate, UserUpdate

logger = structlog.get_logger(__name__)


class UserService(SQLAlchemyService[UserModel, UserCreate, UserUpdate, User]):
    def __init__(self, db: Database):
        repo = UserRepository(db)
        super().__init__(repo, User)

    async def startup(self):
        logger.info("User service started")

    async def shutdown(self):
        logger.info("User service stopped")

    async def get_role(self, id: int) -> str | None:
        return await self.repo.get_role(id)
    
    async def set_role(self, id: int, role: str) -> None:
        return await self.repo.set_role(id, role)
    
    async def remove_role(self, id: int) -> None:
        return await self.repo.remove_role(id)
    
    async def get_user_ids_with_role(self, role: str) -> list[int]:
        return await self.repo.get_user_ids_with_role(role)
