from typing import AsyncIterable

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.base import BaseStorage
from aiogram.fsm.strategy import FSMStrategy
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
from app.services.completion import CompletionService
from app.services.context import ContextService
from app.services.context.storage import (
    BaseContextStorage,
    IContextStorage,
    RedisContextStorage,
)
from app.services.instructions import InstructionService
from app.services.users import UserService
from app.services.summary import SummaryService


class ServicesProvider(Provider):
    def __init__(self) -> None:
        super().__init__(scope=Scope.APP)

    @provide(scope=Scope.APP)
    async def database(self) -> AsyncIterable[Database]:
        autoupgrade = True  # or make it depend from cfg.debug
        db = Database(cfg.DATABASE_URL, autoupgrade)
        await db.startup()
        try:
            yield db
        finally:
            await db.shutdown()

    @provide(scope=Scope.APP)
    async def redis(self) -> AsyncIterable[Redis]:
        redis = Redis.from_url(cfg.REDIS_URL)
        yield redis

    @provide(scope=Scope.APP)
    async def fsm_storage(self, redis: Redis) -> AsyncIterable[BaseStorage]:
        redis = redis if not cfg.DEBUG else None  # use memory storage for debug mode
        storage = await setup_fsm_storage(redis)
        yield storage

    @provide(scope=Scope.APP)
    async def dispatcher(self, storage: BaseStorage) -> AsyncIterable[Dispatcher]:
        dispatcher = await setup_dispatcher(storage, fsm_strategy=FSMStrategy.CHAT_TOPIC)
        yield dispatcher

    @provide(scope=Scope.APP)
    async def bot(self) -> AsyncIterable[Bot]:
        bot = await setup_bot(cfg.BOT_TOKEN, defaults={"parse_mode": "HTML"})
        yield bot

    @provide(scope=Scope.APP)
    async def raito(
        self, dp: Dispatcher, storage: BaseStorage, user_svc: UserService
    ) -> AsyncIterable[Raito]:
        raito = await setup_raito(
            dispatcher=dp,
            routers_dir=HANDLERS_DIR,
            user_service=user_svc,
            developers=cfg.DEVELOPERS,
            production=not cfg.DEBUG,
            storage=storage,
        )
        yield raito

    @provide(scope=Scope.APP)
    async def user_service(self, db: Database) -> AsyncIterable[UserService]:
        service = UserService(db, cfg.DEVELOPERS)
        try:
            await service.startup()
            yield service
        finally:
            await service.shutdown()

    @provide(scope=Scope.APP)
    async def context_storage(self, redis: Redis, summary_svc: SummaryService) -> AsyncIterable[IContextStorage]:
        storage = RedisContextStorage(config=cfg, redis=redis, summary_svc=summary_svc)

        yield storage

    @provide(scope=Scope.APP)
    async def context_service(
        self, storage: IContextStorage
    ) -> AsyncIterable[ContextService]:
        service = ContextService(storage)

        try:
            await service.startup()
            yield service
        finally:
            await service.shutdown()

    @provide(scope=Scope.APP)
    async def SummaryService(self) -> AsyncIterable[SummaryService]:
        service = SummaryService(cfg)

        try:
            await service.startup()
            yield service
        finally:
            await service.shutdown()

    @provide(scope=Scope.APP)
    async def instruction_service(
        self, db: Database
    ) -> AsyncIterable[InstructionService]:
        service = InstructionService(db)

        try:
            await service.startup()
            yield service
        finally:
            await service.shutdown()

    @provide(scope=Scope.APP)
    async def completion_service(
        self, instructions_svc: InstructionService
    ) -> AsyncIterable[CompletionService]:
        service = CompletionService(config=cfg, instructions_svc=instructions_svc)

        try:
            await service.startup()
            yield service
        finally:
            await service.shutdown()
