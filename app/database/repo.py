from typing import Generic, Sequence, Type, TypeVar

from pydantic import BaseModel
from sqlalchemy import select

from app.database.database import Database

ID = TypeVar("ID")
ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class SQLAlchemyRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType], db: Database):
        self.model = model
        self.db = db

    async def get(self, id: ID) -> ModelType | None:
        async with self.db.get_session() as session:
            return await session.get(self.model, id)

    async def exists(self, id: ID) -> bool:
        return await self.get(id) is not None

    async def get_where(self, **where) -> ModelType | None:
        async with self.db.get_session() as session:
            query = select(self.model)

            conditions = []
            for key, value in where.items():
                column = getattr(self.model, key, None)
                if column is not None:
                    conditions.append(column == value)
                else:
                    raise ValueError(f"Invalid filter field: {key}")

            if conditions:
                query = query.where(*conditions)

            result = await session.execute(query)
            return result.scalar_one_or_none()

    async def get_all(
        self, limit: int = None, offset: int = None, **where
    ) -> Sequence[ModelType] | None:
        async with self.db.get_session() as session:
            query = select(self.model)

            conditions = []
            for key, value in where.items():
                column = getattr(self.model, key, None)
                if column is not None:
                    conditions.append(column == value)
                else:
                    raise ValueError(f"Invalid filter field: {key}")

            if conditions:
                query = query.where(*conditions)

            if offset:
                query = query.offset(offset)

            if limit:
                query = query.limit(limit)

            result = await session.execute(query)
            return result.scalars().all()

    async def create(self, obj_in: CreateSchemaType) -> ModelType:
        async with self.db.get_session() as session:
            obj = self.model(**obj_in.model_dump())
            session.add(obj)
            await session.flush()
            await session.refresh(obj)
            return obj

    async def update(self, db_obj: ModelType, obj_in: UpdateSchemaType) -> ModelType:
        async with self.db.get_session() as session:
            data = obj_in.model_dump(exclude_unset=True)
            for key, value in data.items():
                setattr(db_obj, key, value)
            session.add(db_obj)
            await session.flush()
            await session.refresh(db_obj)
            return db_obj

    async def delete(self, db_obj: ModelType) -> None:
        async with self.db.get_session() as session:
            await session.delete(db_obj)
            await session.flush()
