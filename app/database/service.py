from typing import Generic, Type, TypeVar

from pydantic import BaseModel

from app.database.repo import SQLAlchemyRepository

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
ReadSchemaType = TypeVar("ReadSchemaType", bound=BaseModel)


class SQLAlchemyService(
    Generic[ModelType, CreateSchemaType, UpdateSchemaType, ReadSchemaType]
):
    def __init__(
        self,
        repo: SQLAlchemyRepository[ModelType, CreateSchemaType, UpdateSchemaType],
        read_schema: Type[ReadSchemaType],
    ):
        self.repo = repo
        self.read_schema = read_schema

    def _to_read_schema(self, obj: ModelType | None) -> ReadSchemaType | None:
        if obj is None:
            return None
        return self.read_schema.model_validate(obj)

    async def get(self, id: int) -> ReadSchemaType | None:
        obj = await self.repo.get(id)
        return self._to_read_schema(obj)

    async def exists(self, id: int) -> bool:
        return await self.repo.exists(id)

    async def get_where(self, **where) -> ReadSchemaType | None:
        obj = await self.repo.get_where(**where)
        return self._to_read_schema(obj)

    async def get_all(
        self, limit: int = None, offset: int = None, **where
    ) -> list[ReadSchemaType]:
        objs = await self.repo.get_all(limit=limit, offset=offset, **where)
        return [self._to_read_schema(obj) for obj in objs]

    async def create(self, data: CreateSchemaType) -> ReadSchemaType:
        obj = await self.repo.create(data)
        return self._to_read_schema(obj)

    async def update(self, id: int, data: UpdateSchemaType) -> ReadSchemaType | None:
        db_obj = await self.repo.get(id)
        if not db_obj:
            return None
        updated = await self.repo.update(db_obj, data)
        return self._to_read_schema(updated)

    async def delete(self, id: int) -> bool:
        db_obj = await self.repo.get(id)
        if not db_obj:
            return False
        await self.repo.delete(db_obj)
        return True
