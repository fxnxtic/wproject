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


async def setup_fsm_storage(
    redis: Redis | None = None, **kwargs
) -> RedisStorage | MemoryStorage:
    storage = RedisStorage(redis) if redis else MemoryStorage()
    return storage


async def setup_dispatcher(storage: BaseStorage, **kwargs) -> Dispatcher:
    dp = Dispatcher(storage=storage, **kwargs)

    return dp


async def setup_bot(bot_token: str, bot_api_url: str, defaults: dict | None = None, **kwargs) -> Bot:
    session = None
    if bot_api_url != c.BOT_API_URL:
        session = AiohttpSession(api=TelegramAPIServer.from_base(bot_api_url))

    default = DefaultBotProperties(**defaults) if defaults else None

    bot = Bot(token=bot_token, session=session, default=default**kwargs)

    return bot


async def setup_raito(
    dispatcher: Dispatcher,
    routers_dir: str | Path,
    *,
    developers: list[int] | None = None,
    locales: list[str] | None = None,
    production: bool = True,
    configuration: RaitoConfiguration | None = None,
    storage: BaseStorage | None = None,
) -> Raito:
    raito = Raito(
        dispatcher=dispatcher,
        routers_dir=routers_dir,
        developers=developers,
        locales=locales,
        production=production,
        configuration=configuration,
        storage=storage,
    )

    return raito
