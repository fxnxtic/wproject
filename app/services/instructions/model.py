from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, String, Integer,BigInteger, ForeignKey

from app.database import ModelBase


class InstructionModel(ModelBase):
    __tablename__ = "instructions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    author_id = Column(BigInteger, ForeignKey("users.id"))
    prompt = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )
