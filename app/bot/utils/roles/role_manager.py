from raito.plugins.roles import RoleManager, RoleData

from .roles import AVAILABLE_ROLES, AVAILABLE_ROLES_BY_SLUG


class CustomRoleManager(RoleManager):
    @property
    def available_roles(self) -> list[RoleData]:
        """Get a list of available roles.

        :returns: A list of roles
        """
        return AVAILABLE_ROLES

    def get_role_data(self, slug: str) -> RoleData:
        """Get data of specified role.

        :returns: A data of role
        :raises: ...
        """
        return AVAILABLE_ROLES_BY_SLUG[slug]