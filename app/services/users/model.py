from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, String, BigInteger

from app.database import ModelBase


class UserModel(ModelBase):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True)
    role = Column(String, nullable=False, default="user")
    inviter_id = Column(BigInteger, nullable=True)
    firstname = Column(String, nullable=True)
    locale = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )
