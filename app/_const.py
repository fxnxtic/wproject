import os

ALEMBIC_INI_PATH = os.path.join(os.path.dirname(__file__), "../alembic.ini")

BOT_API_URL="https://api.telegram.org"

MUTE_LOGGERS = [
    "aiogram.event",
    "sqlalchemy.engine"
]

DEVELOPERS = []
DEBUG = True