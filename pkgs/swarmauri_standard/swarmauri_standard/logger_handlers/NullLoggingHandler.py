import logging
from typing import Literal

from swarmauri_base.logger_handlers.HandlerBase import HandlerBase
from swarmauri_base.ObserveBase import ObserveBase


@ObserveBase.register_model()
class NullLoggingHandler(HandlerBase):
    """
    A no-op handler that silently ignores all logging records.

    This handler is useful for disabling logging in libraries or specific components
    of an application. It uses Python's built-in NullHandler to discard all log
    messages without any processing.

    Attributes
    ----------
    type : Literal["NullLoggingHandler"]
        The type identifier for this handler.
    level : int
        The logging level threshold (inherited from HandlerBase).
    formatter : Optional[Union[str, FullUnion[FormatterBase]]]
        The formatter to use (inherited from HandlerBase, but not used in this handler).
    """

    type: Literal["NullLoggingHandler"] = "NullLoggingHandler"

    def compile_handler(self) -> logging.Handler:
        """
        Compiles a NullHandler that discards all logging records.

        The NullHandler is a special handler in the Python logging module that
        silently discards all log records without any formatting or output.

        Returns
        -------
        logging.Handler
            A configured NullHandler instance.
        """
        # Create a NullHandler which discards all logging records
        handler = logging.NullHandler()

        # Although this handler discards all messages, we still set the level
        # to maintain consistent behavior with the base class
        handler.setLevel(self.level)

        # No formatter is needed since messages are discarded,
        # but we could add one for consistency if required

        return handler
