from logging import NullHandler
from typing import Literal

from swarmauri_base.logger_handlers.HandlerBase import HandlerBase
from swarmauri_core.ComponentBase import ComponentBase


@ComponentBase.register_type(HandlerBase, "NullLoggingHandler")
class NullLoggingHandler(HandlerBase):
    """
    A no-op handler that silently discards all logging records.

    This handler uses Python's built-in NullHandler to ignore all logging messages,
    which is useful for disabling logging in libraries or when logging output is not needed.
    """

    type: Literal["NullLoggingHandler"] = "NullLoggingHandler"

    def compile_handler(self) -> NullHandler:
        """
        Creates and configures a NullHandler that ignores all log records.

        Returns:
            NullHandler: A configured logging handler that discards all messages.
        """
        # Create a NullHandler instance which will discard all log records
        handler = NullHandler()

        # Even though this handler discards messages, we still set the level
        # to maintain consistency with the base class interface
        handler.setLevel(self.level)

        # No need to set a formatter since messages are discarded,
        # but we could set one for consistency if needed

        return handler
