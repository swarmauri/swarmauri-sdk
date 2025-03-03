from typing import Optional, Union, List
from logging import Logger, Handler, Formatter, getLogger, INFO, StreamHandler

glogger = getLogger("glogger")
glogger.setLevel(level=INFO)
glogger.propagate = False

if not glogger.handlers:
    console_handler = StreamHandler()
    formatter = Formatter("[%(name)s][%(levelname)s] %(message)s")
    console_handler.setFormatter(formatter)
    glogger.addHandler(console_handler)


def set_default_log_level(log_level: int) -> None:
    """
    Update the class-level default log level.
    """
    glogger.setLevel(log_level)
    glogger.info(f"Default log level updated to: {log_level}")


def set_default_logger(logger: Optional[Logger]) -> None:
    """
    Update the class-level default logger.
    """
    glogger.default_logger = logger
    glogger.info(f"Default logger updated to: {logger}")


def set_default_handlers(handlers: Union[Handler, List[Handler]]) -> None:
    """
    Update the class-level default handlers.
    """
    glogger.default_handlers = handlers
    glogger.info(f"Default handlers updated to: {handlers}")


def set_default_formatter(formatter: Formatter) -> None:
    """
    Update the class-level default formatter.
    """
    glogger.default_formatter = formatter
    glogger.info("Default formatter updated.")
