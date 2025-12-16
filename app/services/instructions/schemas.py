from datetime import datetime

from pydantic import BaseModel


class Instruction(BaseModel):
    id: int
    author_id: int
    prompt: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class InstructionCreate(BaseModel):
    author_id: int
    prompt: str
    

class InstructionUpdate(BaseModel):
    ...
