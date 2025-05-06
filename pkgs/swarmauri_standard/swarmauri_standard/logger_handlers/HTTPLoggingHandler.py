import logging
import http.client
import urllib.parse
from typing import Optional, Union, Literal, Dict, Any, Tuple
from swarmauri_base import FullUnion
from swarmauri_base.logger_formatters.FormatterBase import FormatterBase
from swarmauri_base.logger_handlers.HandlerBase import HandlerBase
from swarmauri_core.ComponentBase import ComponentBase


@ComponentBase.register_type(HandlerBase, "HTTPLoggingHandler")
class HTTPLoggingHandler(HandlerBase):
    """
    A logging handler that sends log records to an HTTP endpoint.
    
    This handler supports both GET and POST methods for sending log data,
    and includes options for timeouts and basic authentication.
    """
    type: Literal["HTTPLoggingHandler"] = "HTTPLoggingHandler"
    
    # Required attributes
    host: str
    url: str
    method: Literal["GET", "POST"] = "GET"
    
    # Optional attributes
    timeout: Optional[int] = None
    credentials: Optional[Tuple[str, str]] = None
    
    # HTTP headers to use when sending requests
    headers: Dict[str, str] = {}
    
    def __init__(
        self,
        host: str,
        url: str,
        method: Literal["GET", "POST"] = "GET",
        level: int = logging.INFO,
        formatter: Optional[Union[str, FullUnion[FormatterBase]]] = None,
        timeout: Optional[int] = None,
        credentials: Optional[Tuple[str, str]] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        """
        Initialize the HTTP logging handler.
        
        Args:
            host: The host to connect to (e.g., "example.com")
            url: The URL path to send logs to (e.g., "/log")
            method: HTTP method to use ("GET" or "POST")
            level: Logging level
            formatter: Log formatter to use
            timeout: Connection timeout in seconds
            credentials: Tuple of (username, password) for basic auth
            headers: Dictionary of HTTP headers to include in requests
        """
        super().__init__(level=level, formatter=formatter)
        self.host = host
        self.url = url
        self.method = method
        self.timeout = timeout
        self.credentials = credentials
        self.headers = headers or {}
    
    def compile_handler(self) -> logging.Handler:
        """
        Compiles and returns a logging.handlers.HTTPHandler with the configured settings.
        
        Returns:
            A configured HTTP handler for logging
        """
        # Create a custom HTTPHandler that supports our additional features
        handler = HTTPHandlerExtended(
            host=self.host,
            url=self.url,
            method=self.method,
            timeout=self.timeout,
            credentials=self.credentials,
            headers=self.headers
        )
        
        # Set the logging level
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


class HTTPHandlerExtended(logging.Handler):
    """
    Extended HTTP handler that supports timeouts, credentials, and custom headers.
    
    This class extends the standard logging.handlers.HTTPHandler to provide
    additional functionality needed for the HTTPLoggingHandler.
    """
    
    def __init__(
        self, 
        host: str, 
        url: str, 
        method: str = "GET",
        timeout: Optional[int] = None,
        credentials: Optional[Tuple[str, str]] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        """
        Initialize the extended HTTP handler.
        
        Args:
            host: The host to connect to
            url: The URL path to send logs to
            method: HTTP method to use ("GET" or "POST")
            timeout: Connection timeout in seconds
            credentials: Tuple of (username, password) for basic auth
            headers: Dictionary of HTTP headers to include in requests
        """
        super().__init__()
        self.host = host
        self.url = url
        self.method = method
        self.timeout = timeout
        self.credentials = credentials
        self.headers = headers or {}
    
    def mapLogRecord(self, record: logging.LogRecord) -> Dict[str, Any]:
        """
        Map the log record to a dictionary that can be sent via HTTP.
        
        Args:
            record: The log record to map
            
        Returns:
            Dictionary containing the log record data
        """
        # Create a copy of the record's attributes
        record_dict = {
            'name': record.name,
            'level': record.levelname,
            'pathname': record.pathname,
            'lineno': record.lineno,
            'msg': record.getMessage(),
            'args': str(record.args),
            'exc_info': record.exc_info,
            'func': record.funcName
        }
        
        # Add formatted message if a formatter is set
        if self.formatter:
            record_dict['formatted'] = self.formatter.format(record)
            
        return record_dict
    
    def emit(self, record: logging.LogRecord) -> None:
        """
        Emit a log record by sending it to the configured HTTP endpoint.
        
        Args:
            record: The log record to emit
        """
        try:
            # Map the log record to a dictionary
            data = self.mapLogRecord(record)
            
            # Create HTTP connection with optional timeout
            if self.timeout:
                connection = http.client.HTTPConnection(
                    self.host, 
                    timeout=self.timeout
                )
            else:
                connection = http.client.HTTPConnection(self.host)
            
            # Prepare headers
            headers = self.headers.copy()
            
            # Add basic auth if credentials are provided
            if self.credentials:
                import base64
                auth_str = f"{self.credentials[0]}:{self.credentials[1]}"
                auth_bytes = auth_str.encode('ascii')
                base64_bytes = base64.b64encode(auth_bytes)
                base64_auth = base64_bytes.decode('ascii')
                headers['Authorization'] = f'Basic {base64_auth}'
            
            # Send the request based on the method
            if self.method == "GET":
                # For GET, encode the data in the URL
                url = self.url
                if data:
                    url = f"{url}?{urllib.parse.urlencode(data)}"
                connection.request("GET", url, headers=headers)
            else:
                # For POST, encode the data in the body
                body = urllib.parse.urlencode(data).encode('utf-8')
                headers['Content-Type'] = 'application/x-www-form-urlencoded'
                headers['Content-Length'] = str(len(body))
                connection.request("POST", self.url, body=body, headers=headers)
            
            # Get the response (but we don't do anything with it)
            response = connection.getresponse()
            response.read()  # Read and discard the response body
            connection.close()
            
        except Exception:
            # If an error occurs during emission, call handleError
            self.handleError(record)