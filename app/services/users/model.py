from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, String, Integer

from app.database import ModelBase


class UserModel(ModelBase):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(String, nullable=False, default="user")
    inviter_id = Column(Integer, nullable=True)
    firstname = Column(String, nullable=True)
    locale = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )
