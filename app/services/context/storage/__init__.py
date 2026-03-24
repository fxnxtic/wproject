from .protocol import IContextStorage
from .redis import RedisContextStorage

STORAGE_MODE = {
    "redis": RedisContextStorage,
}

__all__ = [
    "IContextStorage",
    "RedisContextStorage",
    "STORAGE_MODE",
]
