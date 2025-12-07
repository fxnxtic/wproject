from raito.plugins.roles.providers.protocol import IRoleProvider

from app.services.users import UserService

class UserServiceRoleProvider(IRoleProvider):
    def __init__(self, user_svc: UserService):
        self.user_svc = user_svc

    async def get_role(self, bot_id: int, user_id: int) -> str | None:
        return await self.user_svc.get_role(user_id)
    
    async def set_role(self, bot_id: int, user_id: int, role: str) -> None:
        await self.user_svc.set_role(user_id, role)

    async def remove_role(self, bot_id: int, user_id: int) -> None:
        return await self.user_svc.remove_role(user_id)
    
    async def get_users(self, bot_id: int, role: str) -> list[int]:
        return await self.user_svc.get_user_ids_with_role(role)
