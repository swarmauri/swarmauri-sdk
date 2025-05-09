import logging
import socket
from logging.handlers import SysLogHandler
from typing import Optional, Union, Literal, Dict, Any, Tuple

from swarmauri_base import FullUnion
from swarmauri_base.logger_formatters.FormatterBase import FormatterBase
from swarmauri_base.logger_handlers.HandlerBase import HandlerBase
from swarmauri_core.ComponentBase import ComponentBase


@ComponentBase.register_type(HandlerBase, "SysLogLoggingHandler")
class SysLogLoggingHandler(HandlerBase):
    """
    Handler that forwards logging records to a remote or local syslog daemon.

    This handler uses Python's SysLogHandler to send logs to a syslog server,
    which can be either local or remote, configurable by address and facility.

    Attributes
    ----------
    type : Literal["SysLogLoggingHandler"]
        Type identifier for the handler.
    level : int
        The logging level threshold.
    formatter : Optional[Union[str, FullUnion[FormatterBase]]]
        The formatter to use for formatting log messages.
    address : Union[str, Tuple[str, int]]
        Either a string containing a Unix domain socket path or a tuple with host and port.
    facility : str
        The syslog facility to use. Must be one of the predefined SysLogHandler facility names.
    socktype : Optional[str]
        Socket type, either 'udp' or 'tcp'. Defaults to 'udp' if not specified.
    """

    type: Literal["SysLogLoggingHandler"] = "SysLogLoggingHandler"
    level: int = logging.INFO
    formatter: Optional[Union[str, FullUnion[FormatterBase]]] = None
    address: Union[str, Tuple[str, int]] = "/dev/log"  # Default Unix socket on Linux
    facility: str = "user"  # Default facility
    socktype: Optional[str] = None  # Default is UDP

    # Mapping of facility names to their corresponding values
    _FACILITY_MAP: Dict[str, int] = {
        "kern": SysLogHandler.LOG_KERN,
        "user": SysLogHandler.LOG_USER,
        "mail": SysLogHandler.LOG_MAIL,
        "daemon": SysLogHandler.LOG_DAEMON,
        "auth": SysLogHandler.LOG_AUTH,
        "syslog": SysLogHandler.LOG_SYSLOG,
        "lpr": SysLogHandler.LOG_LPR,
        "news": SysLogHandler.LOG_NEWS,
        "uucp": SysLogHandler.LOG_UUCP,
        "cron": SysLogHandler.LOG_CRON,
        "local0": SysLogHandler.LOG_LOCAL0,
        "local1": SysLogHandler.LOG_LOCAL1,
        "local2": SysLogHandler.LOG_LOCAL2,
        "local3": SysLogHandler.LOG_LOCAL3,
        "local4": SysLogHandler.LOG_LOCAL4,
        "local5": SysLogHandler.LOG_LOCAL5,
        "local6": SysLogHandler.LOG_LOCAL6,
        "local7": SysLogHandler.LOG_LOCAL7,
    }

    def _get_facility_value(self) -> int:
        """
        Convert the facility name to its corresponding integer value.

        Returns
        -------
        int
            The facility value as defined in SysLogHandler.

        Raises
        ------
        ValueError
            If the facility name is not recognized.
        """
        if self.facility not in self._FACILITY_MAP:
            valid_facilities = ", ".join(self._FACILITY_MAP.keys())
            raise ValueError(
                f"Invalid facility: {self.facility}. Must be one of: {valid_facilities}"
            )
        return self._FACILITY_MAP[self.facility]

    def _parse_address(self) -> Union[str, Tuple[str, int]]:
        """
        Parse the address attribute to ensure it's in the correct format.

        Returns
        -------
        Union[str, Tuple[str, int]]
            The parsed address, either a Unix socket path or (host, port) tuple.
        """
        if isinstance(self.address, str):
            # Check if the address is in host:port format
            if ":" in self.address:
                host, port_str = self.address.split(":", 1)
                try:
                    port = int(port_str)
                    return (host, port)
                except ValueError:
                    # If port is not an integer, assume it's a Unix socket path
                    return self.address
            return self.address
        return self.address

    def compile_handler(self) -> logging.Handler:
        """
        Compile a SysLogHandler with the configured parameters.

        This method creates a SysLogHandler instance using the specified address
        and facility, and configures it with the appropriate log level and formatter.

        Returns
        -------
        logging.Handler
            A configured SysLogHandler instance.
        """
        address = self._parse_address()
        facility = self._get_facility_value()

        # Determine socket type if specified
        socket_type = None
        if self.socktype:
            if self.socktype.lower() == "tcp":
                socket_type = socket.SOCK_STREAM
            elif self.socktype.lower() == "udp":
                socket_type = socket.SOCK_DGRAM
            else:
                raise ValueError(
                    f"Invalid socket type: {self.socktype}. Must be 'tcp' or 'udp'."
                )

        try:
            # Create the handler with the appropriate parameters
            if socket_type is not None and isinstance(address, tuple):
                # Only use socket_type if address is a network address (host, port)
                handler = SysLogHandler(
                    address=address, facility=facility, socktype=socket_type
                )
            else:
                handler = SysLogHandler(address=address, facility=facility)

            # Set the log level
            handler.setLevel(self.level)

            # Configure the formatter
            if self.formatter:
                if isinstance(self.formatter, str):
                    handler.setFormatter(logging.Formatter(self.formatter))
                else:
                    handler.setFormatter(self.formatter.compile_formatter())
            else:
                # Default formatter for syslog (typically simpler than console output)
                default_formatter = logging.Formatter(
                    "%(name)s[%(process)d]: %(levelname)s %(message)s"
                )
                handler.setFormatter(default_formatter)

            return handler
        except (socket.error, OSError) as e:
            # Handle connection errors gracefully
            # Fall back to a StreamHandler to avoid breaking the application
            import sys

            fallback_handler = logging.StreamHandler(sys.stderr)
            fallback_handler.setLevel(self.level)
            fallback_handler.setFormatter(
                logging.Formatter(
                    f"[SYSLOG ERROR: {str(e)}] %(name)s: %(levelname)s %(message)s"
                )
            )
            return fallback_handler
