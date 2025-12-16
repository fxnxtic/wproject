from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram.fsm.storage.base import BaseStorage
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from raito import Raito
from raito.utils.configuration import RaitoConfiguration
from redis.asyncio import Redis

import app._const as c
from app.bot.middlewares import apply_middleware_to_all, HandleUpdatesMiddleware
from app.bot.utils.roles import CustomRoleManager, UserServiceRoleProvider
from app.services.users import UserService


async def setup_fsm_storage(redis: Redis | None = None) -> RedisStorage | MemoryStorage:
    storage = RedisStorage(redis) if redis else MemoryStorage()
    return storage


async def setup_dispatcher(storage: BaseStorage, **kwargs) -> Dispatcher:
    dp = Dispatcher(storage=storage, **kwargs)

    apply_middleware_to_all(dp, HandleUpdatesMiddleware())

    return dp


async def setup_bot(
    bot_token: str,
    bot_api_url: str | None = None,
    defaults: dict | None = None,
    **kwargs,
) -> Bot:
    session = None
    if isinstance(bot_api_url, str) and bot_api_url != c.BOT_API_URL:
        session = AiohttpSession(api=TelegramAPIServer.from_base(bot_api_url))

    default = DefaultBotProperties(**defaults) if defaults else None

    bot = Bot(token=bot_token, session=session, default=default, **kwargs)

    return bot


async def setup_raito(
    dispatcher: Dispatcher,
    routers_dir: str | Path,
    user_service: UserService,
    *,
    developers: list[int] | None = None,
    production: bool = True,
    storage: BaseStorage | None = None,
) -> Raito:
    configuration = RaitoConfiguration(
        role_manager=CustomRoleManager(provider=UserServiceRoleProvider(user_service))
    )
    raito = Raito(
        dispatcher=dispatcher,
        routers_dir=routers_dir,
        developers=developers,
        production=production,
        configuration=configuration,
        storage=storage,
    )

    return raito
