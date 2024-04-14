import logging
import sys

from core.settings import LogSettings
from loguru import logger


def setup_logging() -> logging.Logger:
    """Setting up logging in the application.

    In this case, there is an option to use logo ru.
    https://github.com/Delgan/loguru
    """
    settings = LogSettings()
    if settings.guru:
        logger.configure(
            **{
                "handlers": [
                    {
                        "sink": sys.stderr,
                        "level": settings.level,
                        "backtrace": settings.traceback,
                    },
                ],
            }
        )
        logger.info("Logging with Guru mode enabled")
        return logger
    logging.basicConfig(level=settings.log_level)
    loger = logging.getLogger(__name__)
    logging.info("Logging with logging.basicConfig")
    return loger
