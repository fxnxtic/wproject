from contextlib import asynccontextmanager
import traceback

import structlog
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.database.migrations import upgrade_head

logger = structlog.get_logger(__name__)


class Database:
    def __init__(self, db_url: str, upgrade: bool = False, raise_errors: bool = False):
        self.db_url = db_url
        self.upgrade = upgrade
        self.raise_errors = raise_errors

        self.engine: AsyncEngine = create_async_engine(
            self.db_url,
            echo=False,
            pool_size=10,
            max_overflow=20,
        )

        self.sessionmaker = async_sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )

    async def startup(self):
        if self.upgrade:
            await upgrade_head()
        else:
            logger.warning("Skipping database upgrade")
        logger.info("Database started")

    async def shutdown(self):
        await self.engine.dispose()
        logger.info("Database stopped")

    @asynccontextmanager
    async def get_session(self):
        session = self.sessionmaker()
        try:
            yield session
            await session.commit()
        except Exception:
            logger.error(traceback.format_exc())
            await session.rollback()
            if self.raise_errors:
                raise
        finally:
            await session.close()
