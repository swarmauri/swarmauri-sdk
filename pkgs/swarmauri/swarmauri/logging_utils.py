import logging
import os

SWARMAURI_LOG_LEVEL = 99
logging.addLevelName(SWARMAURI_LOG_LEVEL, "SWARMAURI")


def swarmauri(self, message, *args, **kwargs):
    if self.isEnabledFor(SWARMAURI_LOG_LEVEL):
        self._log(SWARMAURI_LOG_LEVEL, message, args, **kwargs)


logging.Logger.swarmauri = swarmauri


def get_logger(name: str) -> logging.Logger:
    """Return a logger configured for Swarmauri logging."""
    logger = logging.getLogger(name)

    env_level = os.getenv("SWARMAURI_LOG_LEVEL")
    if env_level:
        try:
            level = int(env_level)
        except ValueError:
            level = SWARMAURI_LOG_LEVEL
        logger.setLevel(level)

    return logger
