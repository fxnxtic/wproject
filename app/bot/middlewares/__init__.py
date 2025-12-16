from aiogram import Router, BaseMiddleware

from .updates import HandleUpdatesMiddleware

__all__ = ["apply_middleware_to_all", "HandleUpdatesMiddleware"]


def apply_middleware_to_all(route: Router, mw: BaseMiddleware):
        for attr in dir(route):
            if not attr.startswith(("_", "update")) and hasattr(getattr(route, attr), "middleware"):
                getattr(route, attr).middleware(mw)
