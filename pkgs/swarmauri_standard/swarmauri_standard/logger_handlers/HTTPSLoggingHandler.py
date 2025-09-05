import http.client
import json
import logging
import ssl
from typing import Any, Dict, Literal, Optional, Union

from swarmauri_base import FullUnion
from swarmauri_base.logger_formatters.FormatterBase import FormatterBase
from swarmauri_base.logger_handlers.HandlerBase import HandlerBase
from swarmauri_base.ObserveBase import ObserveBase


@ObserveBase.register_model()
class HTTPSLoggingHandler(HandlerBase):
    """
    A logging handler that sends log records over HTTPS to a specified endpoint.

    This handler securely transmits log records to a remote server using HTTPS,
    with support for client certificates and custom SSL/TLS configurations.
    """

    type: Literal["HTTPSLoggingHandler"] = "HTTPSLoggingHandler"

    # HTTPS connection settings
    host: str
    url: str
    method: str = "POST"
    port: int = 443

    # SSL/TLS configuration
    ssl_context: Optional[Dict[str, Any]] = None
    cert_file: Optional[str] = None
    key_file: Optional[str] = None
    verify_ssl: bool = True

    # Additional settings
    timeout: int = 5
    headers: Dict[str, str] = {"Content-Type": "application/json"}
    formatter: Optional[Union[str, FullUnion[FormatterBase]]] = None

    def compile_handler(self) -> logging.Handler:
        """
        Creates and configures an HTTPS logging handler.

        Returns:
            logging.Handler: A configured logging handler for HTTPS transmission.
        """
        # Create a custom handler that sends log records over HTTPS
        handler = _HTTPSHandler(
            host=self.host,
            url=self.url,
            method=self.method,
            port=self.port,
            ssl_context=self.ssl_context,
            cert_file=self.cert_file,
            key_file=self.key_file,
            verify_ssl=self.verify_ssl,
            timeout=self.timeout,
            headers=self.headers,
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
            default_formatter = logging.Formatter(
                "[%(name)s][%(levelname)s] %(message)s"
            )
            handler.setFormatter(default_formatter)

        return handler


class _HTTPSHandler(logging.Handler):
    """
    Internal handler class that handles the actual HTTPS transmission of log records.
    """

    def __init__(
        self,
        host: str,
        url: str,
        method: str = "POST",
        port: int = 443,
        ssl_context: Optional[Dict[str, Any]] = None,
        cert_file: Optional[str] = None,
        key_file: Optional[str] = None,
        verify_ssl: bool = True,
        timeout: int = 5,
        headers: Dict[str, str] = None,
    ):
        """
        Initialize the HTTPS handler.

        Args:
            host: The remote host to connect to.
            url: The URL path on the remote host.
            method: The HTTP method to use (default: POST).
            port: The port to connect to (default: 443).
            ssl_context: Dictionary of SSL context parameters.
            cert_file: Path to client certificate file.
            key_file: Path to client private key file.
            verify_ssl: Whether to verify SSL certificates (default: True).
            timeout: Connection timeout in seconds (default: 5).
            headers: HTTP headers to include in the request.
        """
        super().__init__()
        self.host = host
        self.url = url
        self.method = method
        self.port = port
        self.ssl_context = ssl_context
        self.cert_file = cert_file
        self.key_file = key_file
        self.verify_ssl = verify_ssl
        self.timeout = timeout
        self.headers = headers or {"Content-Type": "application/json"}

    def _create_ssl_context(self) -> ssl.SSLContext:
        """
        Create an SSL context based on the provided configuration.

        Returns:
            ssl.SSLContext: The configured SSL context.
        """
        # Create a default SSL context with appropriate security settings
        context = ssl.create_default_context()

        # Configure certificate verification
        if not self.verify_ssl:
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

        # Load client certificates if provided
        if self.cert_file:
            context.load_cert_chain(certfile=self.cert_file, keyfile=self.key_file)

        # Apply any additional SSL context parameters
        if self.ssl_context:
            for key, value in self.ssl_context.items():
                if hasattr(context, key):
                    setattr(context, key, value)

        return context

    def emit(self, record: logging.LogRecord) -> None:
        """
        Send the log record to the specified HTTPS endpoint.

        Args:
            record: The log record to transmit.
        """
        try:
            # Format the record
            msg = self.format(record)

            # Prepare the payload
            payload = {
                "message": msg,
                "level": record.levelname,
                "logger": record.name,
                "timestamp": record.created,
            }

            # Add any extra attributes from the record
            if hasattr(record, "extra") and isinstance(record.extra, dict):
                payload.update(record.extra)

            # Convert payload to JSON
            data = json.dumps(payload).encode("utf-8")

            # Create SSL context
            context = self._create_ssl_context()

            # Establish HTTPS connection
            connection = http.client.HTTPSConnection(
                host=self.host, port=self.port, context=context, timeout=self.timeout
            )

            # Send the request
            connection.request(
                method=self.method, url=self.url, body=data, headers=self.headers
            )

            # Get the response (optional, but good for debugging)
            response = connection.getresponse()

            # Check if the request was successful
            if response.status >= 400:
                logging.getLogger("HTTPSLoggingHandler").warning(
                    f"Failed to send log record: HTTP {response.status} - {response.reason}"
                )

            # Close the connection
            connection.close()

        except Exception as e:
            # Handle any exceptions that occur during emission
            self.handleError(record)
            logging.getLogger("HTTPSLoggingHandler").error(
                f"Error sending log record: {str(e)}"
            )
