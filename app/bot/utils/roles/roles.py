from raito.plugins.roles.roles import ADMINISTRATOR, DEVELOPER, OWNER, _create_role

__all__ = [
    "AVAILABLE_ROLES",
    "AVAILABLE_ROLES_BY_SLUG",
    "ADMINISTRATOR",
    "DEVELOPER",
    "OWNER",
    "USER",
]

USER = _create_role(
    slug="user",
    name="User",
    description="Have access to conversations",
    emoji="👤",
)

AVAILABLE_ROLES = [
    i.filter.data
    for i in [
        ADMINISTRATOR,
        DEVELOPER,
        OWNER,
        USER,
    ]
]
AVAILABLE_ROLES_BY_SLUG = {role.slug: role for role in AVAILABLE_ROLES}
