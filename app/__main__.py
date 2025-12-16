import asyncio
from contextlib import suppress

from aiogram import Bot, Dispatcher
from dishka import make_async_container
from dishka.integrations.aiogram import AiogramProvider, setup_dishka
from raito import Raito
import structlog

from app.core import cfg
from app.core.loggers import init_logging
from app.database import Database
from app.ioc import ServicesProvider

logger = structlog.getLogger(__name__)


async def main():
    init_logging(cfg.MUTE_LOGGERS, debug=cfg.DEBUG)

    logger.info("Starting application...")

    _svc_provider = ServicesProvider()
    _aiogram_provider = AiogramProvider()
    container = make_async_container(
        _svc_provider,
        _aiogram_provider,
    )

    # preload database
    await container.get(Database)
    
    bot = await container.get(Bot)
    raito = await container.get(Raito)
    dp = await container.get(Dispatcher)

    try:
        with suppress(KeyboardInterrupt, asyncio.CancelledError):
            await raito.setup()
            setup_dishka(container, dp)
            await dp.start_polling(bot)
    finally:
        logger.info("Stopping application...")

        with suppress(RuntimeError, asyncio.CancelledError):
            await dp.stop_polling()
            await container.close()


if __name__ == "__main__":
    asyncio.run(main())
