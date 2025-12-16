from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
ALEMBIC_DIR_PATH = BASE_DIR / "alembic"
ALEMBIC_INI_PATH = BASE_DIR / "alembic.ini"

BOT_API_URL="https://api.telegram.org"

MUTE_LOGGERS = [
    "aiogram.event",
    "aiogram.utils.chat_action",
    "sqlalchemy.engine",
    "httpcore.connection",
    "httpcore.http11",
    "watchfiles.main"
]

DEVELOPERS = []
DEBUG = True