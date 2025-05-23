import logging
import socket
from logging.handlers import SysLogHandler
from typing import Literal, Optional, Tuple, Union

from swarmauri_base import FullUnion
from swarmauri_base.logger_formatters.FormatterBase import FormatterBase
from swarmauri_base.logger_handlers.HandlerBase import HandlerBase
from swarmauri_base.ObserveBase import ObserveBase


@ObserveBase.register_model()
@HandlerBase.register_type(HandlerBase, "SysLogLoggingHandler")
class SysLogLoggingHandler(HandlerBase):
    """
    SysLog handler for forwarding logs to a local or remote syslog daemon.

    This handler uses the SysLogHandler from Python's logging module to send logs
    to a syslog server. It can be configured with different addresses, facilities,
    and socket types.
    """

    type: Literal["SysLogLoggingHandler"] = "SysLogLoggingHandler"

    # The address can be a tuple of (host, port) for remote syslog servers
    # or a string representing a Unix domain socket path for local servers
    address: Union[Tuple[str, int], str] = ("localhost", 514)

    # Syslog facility code (defaults to LOG_USER)
    facility: int = SysLogHandler.LOG_USER

    # Socket type: SOCK_DGRAM for UDP (default) or SOCK_STREAM for TCP
    socktype: int = socket.SOCK_DGRAM

    # Optional formatter for the logs
    formatter: Optional[Union[str, FullUnion[FormatterBase]]] = None

    def compile_handler(self) -> logging.Handler:
        """
        Compiles a SysLogHandler with the specified configuration.

        Returns:
            logging.Handler: Configured SysLogHandler instance
        """
        try:
            # Create the SysLogHandler with the specified address and facility
            handler = SysLogHandler(
                address=self.address, facility=self.facility, socktype=self.socktype
            )

            # Set the log level
            handler.setLevel(self.level)

            # Configure the formatter
            if self.formatter:
                if isinstance(self.formatter, str):
                    handler.setFormatter(logging.Formatter(self.formatter))
                else:
                    handler.setFormatter(self.formatter.compile_formatter())
            else:
                # Default formatter for syslog that includes the logger name and level
                default_formatter = logging.Formatter(
                    "%(name)s[%(process)d]: %(levelname)s - %(message)s"
                )
                handler.setFormatter(default_formatter)

            return handler

        except (socket.error, OSError) as e:
            # Log error and fallback to a NullHandler if syslog connection fails
            logging.error(f"Failed to connect to syslog server at {self.address}: {e}")
            return logging.NullHandler()
        except Exception as e:
            # Catch any other unexpected errors
            logging.error(f"Error setting up SysLogHandler: {e}")
            return logging.NullHandler()

    def __str__(self) -> str:
        """
        Returns a string representation of the handler.

        Returns:
            str: String representation
        """
        addr_str = (
            f"{self.address[0]}:{self.address[1]}"
            if isinstance(self.address, tuple)
            else self.address
        )
        return f"SysLogLoggingHandler(address={addr_str}, facility={self.facility}, level={logging.getLevelName(self.level)})"
