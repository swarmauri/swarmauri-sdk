import logging
from swarmauri_core.logging.IHandler import IHandler
from swarmauri_base.ObserveBase import ObserveBase

@ObserveBase.register_model()
class HandlerBase(IHandler, ObserveBase):
    level: int = logging.INFO
    format: str = '[%(name)s][%(levelname)s] %(message)s'

    def compile_handler(self) -> logging.Handler:
        """
        Compiles a logging handler using the specified level and format.
        In this example, a StreamHandler is created.
        """
        handler = logging.StreamHandler()
        handler.setLevel(self.level)
        formatter = logging.Formatter(self.format)
        handler.setFormatter(formatter)
        return handler
