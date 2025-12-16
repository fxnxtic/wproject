from .base import BaseContextStorage, IContextStorage
from .redis import RedisContextStorage

STORAGE_MODE = {
    "redis": RedisContextStorage,
    "memory": BaseContextStorage,
}

__all__ = [
    "BaseContextStorage",
    "IContextStorage",
    "RedisContextStorage",
    "STORAGE_MODE",
]
