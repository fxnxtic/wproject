from enum import StrEnum


class UserRole(StrEnum):
    ADMINISTRATOR = "administrator"
    DEVELOPER = "developer"
    OWNER = "owner"
    USER = "user"
