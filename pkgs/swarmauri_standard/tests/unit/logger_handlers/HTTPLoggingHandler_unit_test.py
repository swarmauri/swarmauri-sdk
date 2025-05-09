import logging
import unittest.mock as mock

import pytest
from swarmauri_base.logger_formatters.FormatterBase import FormatterBase

from swarmauri_standard.logger_handlers.HTTPLoggingHandler import (
    HTTPHandlerExtended,
    HTTPLoggingHandler,
)


@pytest.fixture
def basic_http_handler():
    """
    Create a basic HTTPLoggingHandler for testing.

    Returns:
        A configured HTTPLoggingHandler instance
    """
    return HTTPLoggingHandler(
        host="example.com", url="/logs", method="GET", level=logging.INFO
    )


@pytest.mark.unit
def test_http_handler_initialization():
    """Test that HTTPLoggingHandler initializes with correct attributes."""
    handler = HTTPLoggingHandler(
        host="example.com",
        url="/logs",
        method="POST",
        level=logging.DEBUG,
        timeout=30,
        credentials=("user", "pass"),
        headers={"X-Custom": "Value"},
    )

    assert handler.host == "example.com"
    assert handler.url == "/logs"
    assert handler.method == "POST"
    assert handler.level == logging.DEBUG
    assert handler.timeout == 30
    assert handler.credentials == ("user", "pass")
    assert handler.headers == {"X-Custom": "Value"}
    assert handler.type == "HTTPLoggingHandler"


@pytest.mark.unit
def test_http_handler_default_values():
    """Test that HTTPLoggingHandler uses correct default values."""
    handler = HTTPLoggingHandler(host="example.com", url="/logs")

    assert handler.method == "GET"
    assert handler.level == logging.INFO
    assert handler.timeout is None
    assert handler.credentials is None
    assert handler.headers == {}
    assert handler.formatter is None


@pytest.mark.unit
def test_compile_handler_returns_correct_type(basic_http_handler):
    """Test that compile_handler returns an HTTPHandlerExtended instance."""
    compiled = basic_http_handler.compile_handler()
    assert isinstance(compiled, HTTPHandlerExtended)
    assert compiled.host == "example.com"
    assert compiled.url == "/logs"
    assert compiled.method == "GET"


@pytest.mark.unit
def test_compile_handler_with_string_formatter(basic_http_handler):
    """Test compile_handler with a string formatter."""
    basic_http_handler.formatter = "%(levelname)s: %(message)s"
    compiled = basic_http_handler.compile_handler()

    assert isinstance(compiled.formatter, logging.Formatter)

    # Create a test log record and check formatting
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="Test message",
        args=(),
        exc_info=None,
    )

    formatted = compiled.formatter.format(record)
    assert formatted == "INFO: Test message"


@pytest.mark.unit
def test_compile_handler_with_formatter_object():
    """Test compile_handler with a FormatterBase object."""
    mock_formatter = mock.MagicMock(spec=FormatterBase)
    mock_compiled_formatter = mock.MagicMock(spec=logging.Formatter)
    mock_formatter.compile_formatter.return_value = mock_compiled_formatter

    handler = HTTPLoggingHandler(
        host="example.com", url="/logs", formatter=mock_formatter
    )

    compiled = handler.compile_handler()

    # Verify the formatter was compiled and set
    mock_formatter.compile_formatter.assert_called_once()
    assert compiled.formatter == mock_compiled_formatter


@pytest.mark.unit
def test_compile_handler_default_formatter(basic_http_handler):
    """Test that compile_handler sets a default formatter if none is provided."""
    compiled = basic_http_handler.compile_handler()

    assert isinstance(compiled.formatter, logging.Formatter)

    # Create a test log record and check formatting matches default pattern
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="Test message",
        args=(),
        exc_info=None,
    )

    formatted = compiled.formatter.format(record)
    assert "[test][INFO] Test message" in formatted


@pytest.mark.unit
class TestHTTPHandlerExtended:
    """Unit tests for the HTTPHandlerExtended class."""

    @pytest.fixture
    def extended_handler(self):
        """Create a basic HTTPHandlerExtended for testing."""
        return HTTPHandlerExtended(host="example.com", url="/logs", method="GET")

    def test_initialization(self):
        """Test that HTTPHandlerExtended initializes with correct attributes."""
        handler = HTTPHandlerExtended(
            host="example.com",
            url="/logs",
            method="POST",
            timeout=30,
            credentials=("user", "pass"),
            headers={"X-Custom": "Value"},
        )

        assert handler.host == "example.com"
        assert handler.url == "/logs"
        assert handler.method == "POST"
        assert handler.timeout == 30
        assert handler.credentials == ("user", "pass")
        assert handler.headers == {"X-Custom": "Value"}

    def test_map_log_record(self, extended_handler):
        """Test that mapLogRecord correctly maps a log record to a dictionary."""
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="/path/to/file.py",
            lineno=42,
            msg="Test message with %s",
            args=("parameter",),
            exc_info=None,
        )

        mapped = extended_handler.mapLogRecord(record)

        assert mapped["name"] == "test_logger"
        assert mapped["level"] == "INFO"
        assert mapped["pathname"] == "/path/to/file.py"
        assert mapped["lineno"] == 42
        assert mapped["msg"] == "Test message with parameter"
        assert mapped["func"] == "test_map_log_record"  # From the test function name

    def test_map_log_record_with_formatter(self, extended_handler):
        """Test that mapLogRecord includes formatted message when formatter is set."""
        formatter = logging.Formatter("%(levelname)s: %(message)s")
        extended_handler.setFormatter(formatter)

        record = logging.LogRecord(
            name="test_logger",
            level=logging.WARNING,
            pathname="",
            lineno=0,
            msg="Warning message",
            args=(),
            exc_info=None,
        )

        mapped = extended_handler.mapLogRecord(record)

        assert "formatted" in mapped
        assert mapped["formatted"] == "WARNING: Warning message"

    @mock.patch("http.client.HTTPConnection")
    def test_emit_get_method(self, mock_http_connection, extended_handler):
        """Test that emit correctly sends a GET request."""
        # Setup mock connection and response
        mock_conn = mock.MagicMock()
        mock_response = mock.MagicMock()
        mock_http_connection.return_value = mock_conn
        mock_conn.getresponse.return_value = mock_response

        # Create a log record
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        # Emit the record
        extended_handler.emit(record)

        # Verify HTTP connection was created correctly
        mock_http_connection.assert_called_once_with("example.com")

        # Verify a GET request was made with URL parameters
        args, kwargs = mock_conn.request.call_args
        assert args[0] == "GET"
        assert args[1].startswith("/logs?")
        assert "name=test_logger" in args[1]
        assert "level=INFO" in args[1]
        assert "msg=Test+message" in args[1]

    @mock.patch("http.client.HTTPConnection")
    def test_emit_post_method(self, mock_http_connection):
        """Test that emit correctly sends a POST request."""
        # Create handler with POST method
        handler = HTTPHandlerExtended(host="example.com", url="/logs", method="POST")

        # Setup mock connection and response
        mock_conn = mock.MagicMock()
        mock_response = mock.MagicMock()
        mock_http_connection.return_value = mock_conn
        mock_conn.getresponse.return_value = mock_response

        # Create a log record
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        # Emit the record
        handler.emit(record)

        # Verify HTTP connection was created correctly
        mock_http_connection.assert_called_once_with("example.com")

        # Verify a POST request was made with correct headers and body
        args, kwargs = mock_conn.request.call_args
        assert args[0] == "POST"
        assert args[1] == "/logs"
        assert "Content-Type" in kwargs["headers"]
        assert kwargs["headers"]["Content-Type"] == "application/x-www-form-urlencoded"
        assert "Content-Length" in kwargs["headers"]
        assert "body" in kwargs
        assert b"name=test_logger" in kwargs["body"]
        assert b"level=INFO" in kwargs["body"]
        assert b"msg=Test+message" in kwargs["body"]

    @mock.patch("http.client.HTTPConnection")
    def test_emit_with_timeout(self, mock_http_connection):
        """Test that emit uses the timeout when creating the connection."""
        # Create handler with timeout
        handler = HTTPHandlerExtended(host="example.com", url="/logs", timeout=30)

        # Setup mock connection and response
        mock_conn = mock.MagicMock()
        mock_response = mock.MagicMock()
        mock_http_connection.return_value = mock_conn
        mock_conn.getresponse.return_value = mock_response

        # Create a log record
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        # Emit the record
        handler.emit(record)

        # Verify HTTP connection was created with timeout
        mock_http_connection.assert_called_once_with("example.com", timeout=30)
