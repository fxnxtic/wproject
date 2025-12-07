from datetime import datetime

from pydantic import BaseModel


class User(BaseModel):
    id: int
    inviter_id: int
    role: str
    firstname: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    id: int
    role: str | None = None
    inviter_id: int | None = None
    firstname: str | None = None
    locale: str | None = None


class UserUpdate(BaseModel):
    role: str | None = None
    inviter_id: int | None = None
    firstname: str | None = None
    locale: str | None = None
