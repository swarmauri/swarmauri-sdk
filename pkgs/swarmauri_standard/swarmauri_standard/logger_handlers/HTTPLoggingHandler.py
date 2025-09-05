import http.client
from logging.handlers import HTTPHandler
import logging
import urllib.parse
from typing import Dict, Literal, Optional, Union

from swarmauri_base import FullUnion
from swarmauri_base.logger_formatters.FormatterBase import FormatterBase
from swarmauri_base.logger_handlers.HandlerBase import HandlerBase
from swarmauri_base.ObserveBase import ObserveBase


@ObserveBase.register_model()
class HTTPLoggingHandler(HandlerBase):
    """
    Handler for sending log records to an HTTP endpoint.

    This handler sends log records to a specified HTTP endpoint using either GET or POST methods.
    It supports optional timeout and basic authentication credentials.
    """

    type: Literal["HTTPLoggingHandler"] = "HTTPLoggingHandler"

    # HTTP configuration
    host: str
    url: str
    method: Literal["GET", "POST"] = "POST"
    timeout: Optional[float] = None
    credentials: Optional[Dict[str, str]] = None

    # Handler configuration
    level: int = logging.INFO
    formatter: Optional[Union[str, FullUnion[FormatterBase]]] = None

    def compile_handler(self) -> logging.Handler:
        """
        Compiles an HTTP logging handler using the specified configuration.

        Returns:
            logging.Handler: An HTTP handler configured with the specified parameters.
        """
        # Create a custom HTTP handler that includes our timeout and credentials
        handler = self._create_http_handler()

        # Set the log level
        handler.setLevel(self.level)

        # Configure the formatter
        if self.formatter:
            if isinstance(self.formatter, str):
                handler.setFormatter(logging.Formatter(self.formatter))
            else:
                handler.setFormatter(self.formatter.compile_formatter())
        else:
            # Use a default formatter if none is provided
            default_formatter = logging.Formatter(
                "[%(name)s][%(levelname)s] %(message)s"
            )
            handler.setFormatter(default_formatter)

        return handler

    def _create_http_handler(self) -> logging.Handler:
        """
        Creates a custom HTTP handler with support for timeout and credentials.

        Returns:
            logging.Handler: A customized HTTP handler.
        """

        # Create a custom HTTPHandler that supports our additional parameters
        class CustomHTTPHandler(HTTPHandler):
            def __init__(
                self,
                host: str,
                url: str,
                method: str = "POST",
                timeout: Optional[float] = None,
                credentials: Optional[Dict[str, str]] = None,
            ):
                super().__init__(host, url, method)
                self.timeout = timeout
                self.credentials = credentials

            def emit(self, record: logging.LogRecord) -> None:
                """
                Send the log record to the specified HTTP endpoint.

                Args:
                    record: The log record to be sent.
                """
                try:
                    # Format the record
                    msg = self.format(record)

                    # Prepare the connection
                    if self.credentials:
                        # Use basic authentication if credentials are provided
                        headers = {
                            "Authorization": "Basic "
                            + urllib.parse.quote_plus(
                                f"{self.credentials.get('username', '')}:{self.credentials.get('password', '')}"
                            )
                        }
                    else:
                        headers = {}

                    # Establish connection with timeout if specified
                    connection = http.client.HTTPConnection(
                        self.host, timeout=self.timeout
                    )

                    # Send the request based on the method
                    if self.method == "GET":
                        connection.request(
                            "GET",
                            f"{self.url}?message={urllib.parse.quote(msg)}",
                            headers=headers,
                        )
                    else:  # POST
                        headers["Content-type"] = "application/x-www-form-urlencoded"
                        connection.request(
                            "POST",
                            self.url,
                            urllib.parse.urlencode({"message": msg}),
                            headers=headers,
                        )

                    connection.close()

                except (KeyboardInterrupt, SystemExit):
                    raise
                except Exception:
                    self.handleError(record)

        # Create and return our custom handler
        return CustomHTTPHandler(
            host=self.host,
            url=self.url,
            method=self.method,
            timeout=self.timeout,
            credentials=self.credentials,
        )
