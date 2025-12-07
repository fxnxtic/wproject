from app.core.loggers import init_logging
from app.core.settings import Settings

cfg = Settings()

__all__ = ["init_logging", "cfg", "Settings"]
