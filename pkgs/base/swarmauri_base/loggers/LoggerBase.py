import logging
from typing import List, Optional, Any
from pydantic import Field
from swarmauri_core.loggers.ILogger import ILogger
from swarmauri_base.logger_handlers.HandlerBase import HandlerBase
from swarmauri_base.ObserveBase import ObserveBase
from swarmauri_base import FullUnion


@ObserveBase.register_model()
class LoggerBase(ILogger, ObserveBase):
    """LoggerBase is an implementation of ILogger that wraps Python's built-in logging module.

    It compiles a logger with a specified name and attaches either user-provided or default handlers.
    """

    name: str = __name__
    handlers: List[FullUnion[HandlerBase]] = []
    default_level: int = logging.INFO
    default_format: str = "[%(name)s][%(levelname)s] %(message)s"
    logger: Optional[Any] = Field(exclude=True, default=None)

    def model_post_init(self, *args, **kwargs):
        """Initialize the LoggerBase instance.

        This method initializes the logger by compiling a logging.Logger instance with the configured name and handlers.

        Parameters
        ----------
        *args : any
            Positional arguments.
        **kwargs : any
            Keyword arguments.
        """
        self.logger = self.compile_logger(logger_name=self.name)

    def compile_logger(self, logger_name: str = __name__) -> logging.Logger:
        logger = logging.getLogger(logger_name)
        logger.setLevel(self.default_level)

        # Clear existing handlers to avoid stale configurations
        logger.handlers.clear()

        if self.handlers:
            for handler_model in self.handlers:
                handler = handler_model.compile_handler()
                handler.setLevel(self.default_level)
                logger.addHandler(handler)
        else:
            default_handler = logging.StreamHandler()
            default_handler.setLevel(self.default_level)
            default_handler.setFormatter(logging.Formatter(self.default_format))
            logger.addHandler(default_handler)

        logger.propagate = False
        return logger

    def set_level(self, level: int = 20) -> None:
        self.default_level = level
        self.compile_logger(logger_name=self.name)

    def set_format(
        self, format_string: str = "[%(name)s][%(levelname)s] %(message)s"
    ) -> None:
        self.default_format = format_string
        self.compile_logger(logger_name=self.name)

    def debug(self, *args, **kwargs) -> None:
        """Log a debug message.

        Parameters
        ----------
        *args : any
            Positional arguments for the log message.
        **kwargs : any
            Keyword arguments for the log message.
        """
        self.logger.debug(*args, **kwargs)

    def info(self, *args, **kwargs) -> None:
        """Log an info message.

        Parameters
        ----------
        *args : any
            Positional arguments for the log message.
        **kwargs : any
            Keyword arguments for the log message.
        """
        self.logger.info(*args, **kwargs)

    def warning(self, *args, **kwargs) -> None:
        """Log a warning message.

        Parameters
        ----------
        *args : any
            Positional arguments for the log message.
        **kwargs : any
            Keyword arguments for the log message.
        """
        self.logger.warning(*args, **kwargs)

    def error(self, *args, **kwargs) -> None:
        """Log an error message.

        Parameters
        ----------
        *args : any
            Positional arguments for the log message.
        **kwargs : any
            Keyword arguments for the log message.
        """
        self.logger.error(*args, **kwargs)

    def critical(self, *args, **kwargs) -> None:
        """Log a critical message.

        Parameters
        ----------
        *args : any
            Positional arguments for the log message.
        **kwargs : any
            Keyword arguments for the log message.
        """
        self.logger.critical(*args, **kwargs)

    def exception(self, *args, **kwargs) -> None:
        """Log an exception traceback along with an error message.

        Parameters
        ----------
        *args : any
            Positional arguments for the log message.
        **kwargs : any
            Keyword arguments for the log message.
        """
        self.logger.exception(*args, **kwargs)

    def log(self, level: int, *args, **kwargs) -> None:
        """Log a message with a custom numeric level.

        Parameters
        ----------
        level : int
            The numeric logging level.
        *args : any
            Positional arguments for the log message.
        **kwargs : any
            Keyword arguments for the log message.
        """
        self.logger.log(level, *args, **kwargs)
