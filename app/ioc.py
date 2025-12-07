from typing import AsyncIterable

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.base import BaseStorage
from dishka import Provider, Scope, provide
from raito import Raito
from redis.asyncio import Redis

from app.bot.handlers import HANDLERS_DIR
from app.bot.setup import (
    setup_bot,
    setup_dispatcher,
    setup_fsm_storage,
    setup_raito,
)
from app.core import cfg
from app.database import Database
from app.services.users import UserService


class ServicesProvider(Provider):
    def __init__(self) -> None:
        super().__init__(scope=Scope.APP)

    @provide(scope=Scope.APP)
    async def database(self) -> AsyncIterable[Database]:
        autoupgrade = False  # or make it depend from cfg.debug
        db = Database(cfg.db_url, autoupgrade)
        await db.startup()
        try:
            yield db
        finally:
            await db.shutdown()

    @provide(scope=Scope.APP)
    async def redis(self) -> AsyncIterable[Redis]:
        redis = Redis.from_url(cfg.redis_url)
        yield redis

    @provide(scope=Scope.APP)
    async def fsm_storage(self, redis: Redis) -> AsyncIterable[BaseStorage]:
        redis = redis if cfg.debug else None    # use memory storage for debug mode
        storage = await setup_fsm_storage(redis)
        yield storage

    @provide(scope=Scope.APP)
    async def dispatcher(self, storage: BaseStorage) -> AsyncIterable[Dispatcher]:
        dispatcher = await setup_dispatcher(storage)
        yield dispatcher

    @provide(scope=Scope.APP)
    async def bot(self) -> AsyncIterable[Bot]:
        bot = await setup_bot(cfg.bot_token, cfg.bot_api_url)
        yield bot

    @provide(scope=Scope.APP)
    async def raito(self, dp: Dispatcher, storage: BaseStorage) -> AsyncIterable[Raito]:
        raito = await setup_raito(
            dispatcher=dp,
            routers_dir=HANDLERS_DIR,
            developers=cfg.developers,
            locales=["en", "ru"],
            production=not cfg.debug,
            configuration=None,
            storage=storage,
        )
        
        await raito.setup()
        yield raito

    @provide(scope=Scope.APP)
    async def user_service(self, db: Database) -> AsyncIterable[UserService]:
        service = UserService(db)
        try:
            await service.startup()
            yield service
        finally:
            await service.shutdown()
