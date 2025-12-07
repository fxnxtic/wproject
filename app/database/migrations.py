import asyncio
import os
from pathlib import Path

from alembic import command
from alembic.config import Config

import app._const as c
from app.core import cfg

ALEMBIC_INI_PATH = os.path.join(os.path.dirname(__file__), "../alembic.ini")


async def upgrade_head(alembic_path: str | Path = None):
    """Upgrade the database to the latest head revision.

    Args:
        alembic_path: Optional[str | Path], The path to the Alembic configuration file.
            Defaults to c.ALEMBIC_INI_PATH if not provided.

    Returns:
        None
    """
    alembic_path = alembic_path or c.ALEMBIC_INI_PATH

    alembic_cfg = Config(alembic_path)

    alembic_cfg.set_main_option("sqlalchemy.url", cfg.db_url)

    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, command.upgrade, alembic_cfg, "head")
