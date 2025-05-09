import logging
import ssl
import urllib.request
import urllib.error
import socket
from typing import Optional, Union, Dict, Any, Literal, List
from urllib.parse import urlencode

from swarmauri_base import FullUnion
from swarmauri_base.logger_formatters.FormatterBase import FormatterBase
from swarmauri_base.logger_handlers.HandlerBase import HandlerBase
from swarmauri_base.ObserveBase import ObserveBase


@ObserveBase.register_model()
class HTTPSLoggingHandler(HandlerBase):
    """
    A logging handler that sends log records over HTTPS.

    This handler posts log messages to a specified URL using HTTPS protocol,
    with optional support for client certificates and SSL/TLS configuration.
    """

    type: Literal["HTTPSLoggingHandler"] = "HTTPSLoggingHandler"

    # HTTPS connection parameters
    host: str = "localhost"
    url: str = "/log"
    method: str = "POST"
    port: int = 443

    # SSL/TLS configuration
    ssl_context: Optional[Dict[str, Any]] = None
    cert_file: Optional[str] = None
    key_file: Optional[str] = None
    ca_certs: Optional[str] = None
    verify_ssl: bool = True

    # Request headers
    headers: Dict[str, str] = {"Content-Type": "application/x-www-form-urlencoded"}

    # Timeout in seconds
    timeout: float = 5.0

    # Additional request parameters
    additional_params: Dict[str, str] = {}

    def __init__(
        self,
        level: int = logging.INFO,
        formatter: Optional[Union[str, FullUnion[FormatterBase]]] = None,
        host: str = "localhost",
        url: str = "/log",
        method: str = "POST",
        port: int = 443,
        ssl_context: Optional[Dict[str, Any]] = None,
        cert_file: Optional[str] = None,
        key_file: Optional[str] = None,
        ca_certs: Optional[str] = None,
        verify_ssl: bool = True,
        headers: Optional[Dict[str, str]] = None,
        timeout: float = 5.0,
        additional_params: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the HTTPS logging handler with the given parameters.

        Args:
            level: The logging level.
            formatter: The formatter to use for log messages.
            host: The target host to send logs to.
            url: The URL path on the host.
            method: The HTTP method to use (GET, POST, etc.).
            port: The port to connect to.
            ssl_context: SSL context parameters.
            cert_file: Path to client certificate file.
            key_file: Path to client key file.
            ca_certs: Path to CA certificates file.
            verify_ssl: Whether to verify SSL certificates.
            headers: HTTP headers to include in the request.
            timeout: Connection timeout in seconds.
            additional_params: Additional parameters to include in the request.
            **kwargs: Additional keyword arguments.
        """
        super().__init__(level=level, formatter=formatter, **kwargs)
        self.host = host
        self.url = url
        self.method = method
        self.port = port
        self.ssl_context = ssl_context or {}
        self.cert_file = cert_file
        self.key_file = key_file
        self.ca_certs = ca_certs
        self.verify_ssl = verify_ssl
        self.headers = headers or {"Content-Type": "application/x-www-form-urlencoded"}
        self.timeout = timeout
        self.additional_params = additional_params or {}

    def _create_ssl_context(self) -> ssl.SSLContext:
        """
        Create an SSL context with the configured parameters.

        Returns:
            An SSL context configured according to the handler's settings.
        """
        # Create SSL context with appropriate protocol
        context = ssl.create_default_context(
            purpose=ssl.Purpose.CLIENT_AUTH
            if self.cert_file
            else ssl.Purpose.SERVER_AUTH
        )

        # Load client certificate and key if provided
        if self.cert_file:
            context.load_cert_chain(certfile=self.cert_file, keyfile=self.key_file)

        # Load CA certificates if provided
        if self.ca_certs:
            context.load_verify_locations(cafile=self.ca_certs)

        # Configure certificate verification
        if not self.verify_ssl:
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

        # Apply any additional SSL context settings
        for key, value in self.ssl_context.items():
            if hasattr(context, key):
                setattr(context, key, value)

        return context

    def _format_record(self, record: logging.LogRecord) -> Dict[str, str]:
        """
        Format the log record into a dictionary suitable for sending via HTTPS.

        Args:
            record: The log record to format.

        Returns:
            A dictionary containing the formatted log data.
        """
        # Use the handler's formatter to format the record
        if hasattr(self, "formatter") and self.formatter:
            if isinstance(self.formatter, str):
                formatter = logging.Formatter(self.formatter)
            else:
                formatter = self.formatter.compile_formatter()
        else:
            formatter = logging.Formatter("[%(name)s][%(levelname)s] %(message)s")

        formatted_message = formatter.format(record)

        # Create a dictionary with log information
        log_data = {
            "message": formatted_message,
            "level": record.levelname,
            "logger": record.name,
            "timestamp": str(record.created),
        }

        # Add exception info if available
        if record.exc_info:
            log_data["exception"] = self._format_exception(record.exc_info)

        # Add any additional record attributes
        for attr, value in record.__dict__.items():
            if (
                attr not in log_data
                and not attr.startswith("_")
                and isinstance(value, (str, int, float, bool))
            ):
                log_data[attr] = str(value)

        # Add any additional parameters specified in the handler
        log_data.update(self.additional_params)

        return log_data

    def _format_exception(self, exc_info: tuple) -> str:
        """
        Format exception information into a string.

        Args:
            exc_info: Exception information tuple.

        Returns:
            Formatted exception string.
        """
        import traceback

        return "".join(traceback.format_exception(*exc_info))

    def _send_log(self, record: logging.LogRecord) -> None:
        """
        Send the log record over HTTPS.

        Args:
            record: The log record to send.
        """
        try:
            # Format the record
            log_data = self._format_record(record)

            # Create the full URL
            full_url = f"https://{self.host}:{self.port}{self.url}"

            # Create SSL context
            ssl_context = self._create_ssl_context()

            # Prepare request data
            data = urlencode(log_data).encode("utf-8")

            # Create request
            request = urllib.request.Request(
                url=full_url,
                data=data if self.method != "GET" else None,
                headers=self.headers,
                method=self.method,
            )

            # If it's a GET request, append parameters to the URL
            if self.method == "GET":
                request.full_url = f"{full_url}?{urlencode(log_data)}"

            # Send the request
            with urllib.request.urlopen(
                request, context=ssl_context, timeout=self.timeout
            ) as response:
                if response.status not in (200, 201, 202, 204):
                    # Log error if the server didn't accept the log
                    sys_stderr_handler = logging.StreamHandler()
                    sys_stderr_handler.setLevel(logging.ERROR)
                    sys_stderr_handler.setFormatter(logging.Formatter("%(message)s"))
                    error_logger = logging.getLogger("HTTPSLoggingHandler")
                    error_logger.addHandler(sys_stderr_handler)
                    error_logger.error(
                        f"Failed to send log: HTTP {response.status} - {response.read().decode('utf-8')}"
                    )

        except (urllib.error.URLError, socket.error) as e:
            # Handle connection errors
            sys_stderr_handler = logging.StreamHandler()
            sys_stderr_handler.setLevel(logging.ERROR)
            sys_stderr_handler.setFormatter(logging.Formatter("%(message)s"))
            error_logger = logging.getLogger("HTTPSLoggingHandler")
            error_logger.addHandler(sys_stderr_handler)
            error_logger.error(f"Error sending log: {str(e)}")

    def compile_handler(self) -> logging.Handler:
        """
        Compile a logging handler that sends logs over HTTPS.

        Returns:
            A logging handler configured to send logs over HTTPS.
        """

        # Create a custom handler that uses our _send_log method
        class HTTPSHandler(logging.Handler):
            def __init__(self, outer_instance):
                super().__init__()
                self.outer = outer_instance

            def emit(self, record):
                try:
                    self.outer._send_log(record)
                except Exception:
                    self.handleError(record)

        # Create and configure the handler
        handler = HTTPSHandler(self)
        handler.setLevel(self.level)

        # Set formatter
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
