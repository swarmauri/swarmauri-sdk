import logging
from swarmauri_base import FullUnion
from swarmauri_base.logger_formatters.FormatterBase import FormatterBase
from swarmauri_core.logger_handlers.IHandler import IHandler
from swarmauri_base.ObserveBase import ObserveBase
from typing import Optional, Union


@ObserveBase.register_model()
class HandlerBase(IHandler, ObserveBase):
    level: int = logging.INFO
    formatter: Optional[Union[str, FullUnion[FormatterBase]]] = None

    def compile_handler(self) -> logging.Handler:
        """
        Compiles a logging handler using the specified level and format.
        In this example, a StreamHandler is created.
        """
        handler = logging.StreamHandler()
        handler.setLevel(self.level)

        if self.formatter:
            if isinstance(self.formatter, str):
                handler.setFormatter(logging.Formatter(self.formatter))
            else:
                handler.setFormatter(self.formatter.compile_formatter())
        else:
            default_formatter = logging.Formatter(
                "[%(name)s][%(levelname)s] %(message)s"
            )
            handler.setFormatter(default_formatter)

        return handler
