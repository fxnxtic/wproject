import logging
import sys

import structlog


class MuteDropper(logging.Filter):
    def __init__(self, names_to_mute: list[str]):
        super().__init__()
        self.names_to_mute = set(names_to_mute)

    def filter(self, record: logging.LogRecord) -> bool:
        return record.name not in self.names_to_mute


def init_logging(mute_loggers: list[str] | None = None, debug: bool = False) -> None:
    """
    Initializes the logging system.

    Args:
        *mute_loggers (str): The names of loggers to mute.
        debug (bool, optional): Whether to enable debug logging. Defaults to False.
    """
    mute_loggers = [] if mute_loggers is None else mute_loggers

    logging.captureWarnings(True)

    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        stream=sys.stdout,
        format="%(message)s",
    )

    renderer = (
        structlog.dev.ConsoleRenderer(colors=True)
        if debug
        else structlog.processors.JSONRenderer()
    )

    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.add_log_level,
            structlog.processors.format_exc_info,
            renderer,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(MuteDropper(mute_loggers))

    handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            processor=renderer,
            foreign_pre_chain=[
                structlog.stdlib.add_log_level,
                structlog.processors.TimeStamper(fmt="iso"),
            ],
        )
    )

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
