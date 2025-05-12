import logging
import unittest.mock as mock

import pytest
from swarmauri_base.logger_formatters.FormatterBase import FormatterBase

from swarmauri_standard.logger_handlers.HTTPLoggingHandler import HTTPLoggingHandler


@pytest.fixture
def basic_http_handler():
    """
    Creates a basic HTTP logging handler for testing.

    Returns:
        HTTPLoggingHandler: A basic HTTP logging handler instance.
    """
    return HTTPLoggingHandler(
        host="example.com", url="/log", method="POST", level=logging.INFO
    )


@pytest.fixture
def advanced_http_handler():
    """
    Creates an HTTP logging handler with advanced options for testing.

    Returns:
        HTTPLoggingHandler: An HTTP logging handler with timeout and credentials.
    """
    return HTTPLoggingHandler(
        host="example.com",
        url="/log",
        method="GET",
        timeout=5.0,
        credentials={"username": "user", "password": "pass"},
        level=logging.DEBUG,
    )


@pytest.fixture
def mock_formatter():
    """
    Creates a mock formatter for testing.

    Returns:
        mock.Mock: A mocked formatter instance.
    """
    formatter = mock.Mock(spec=FormatterBase)
    mock_logging_formatter = mock.Mock(spec=logging.Formatter)
    formatter.compile_formatter.return_value = mock_logging_formatter
    return formatter


@pytest.mark.unit
def test_init_with_defaults():
    """Tests initialization with default values."""
    handler = HTTPLoggingHandler(host="example.com", url="/log")

    assert handler.host == "example.com"
    assert handler.url == "/log"
    assert handler.method == "POST"  # Default method
    assert handler.timeout is None  # Default timeout
    assert handler.credentials is None  # Default credentials
    assert handler.level == logging.INFO  # Default level
    assert handler.formatter is None  # Default formatter


@pytest.mark.unit
def test_init_with_custom_values():
    """Tests initialization with custom values."""
    handler = HTTPLoggingHandler(
        host="custom.com",
        url="/custom",
        method="GET",
        timeout=10.0,
        credentials={"username": "testuser", "password": "testpass"},
        level=logging.DEBUG,
        formatter="%(levelname)s: %(message)s",
    )

    assert handler.host == "custom.com"
    assert handler.url == "/custom"
    assert handler.method == "GET"
    assert handler.timeout == 10.0
    assert handler.credentials == {"username": "testuser", "password": "testpass"}
    assert handler.level == logging.DEBUG
    assert handler.formatter == "%(levelname)s: %(message)s"


@pytest.mark.unit
def test_type_attribute():
    """Tests the type attribute is correctly set."""
    handler = HTTPLoggingHandler(host="example.com", url="/log")
    assert handler.type == "HTTPLoggingHandler"


@pytest.mark.unit
@mock.patch("http.client.HTTPConnection")
def test_compile_handler_basic(mock_http_connection, basic_http_handler):
    """Tests compiling a basic HTTP handler."""
    # Compile the handler
    compiled_handler = basic_http_handler.compile_handler()

    # Verify the compiled handler is a logging.Handler
    assert isinstance(compiled_handler, logging.Handler)

    # Verify the level is set correctly
    assert compiled_handler.level == logging.INFO

    # Verify the formatter is set (should be a default one)
    assert isinstance(compiled_handler.formatter, logging.Formatter)


@pytest.mark.unit
@mock.patch("http.client.HTTPConnection")
def test_compile_handler_with_string_formatter(
    mock_http_connection, basic_http_handler
):
    """Tests compiling a handler with a string formatter."""
    # Set a string formatter
    basic_http_handler.formatter = "%(levelname)s - %(message)s"

    # Compile the handler
    compiled_handler = basic_http_handler.compile_handler()

    # Verify the formatter is set correctly
    assert isinstance(compiled_handler.formatter, logging.Formatter)
    # We can't easily check the format string as it's not directly accessible


@pytest.mark.unit
@mock.patch("http.client.HTTPConnection")
def test_compile_handler_with_formatter_object(
    mock_http_connection, basic_http_handler, mock_formatter
):
    """Tests compiling a handler with a formatter object."""
    # Set a formatter object
    basic_http_handler.formatter = mock_formatter

    # Compile the handler
    compiled_handler = basic_http_handler.compile_handler()

    # Verify the formatter.compile_formatter method was called
    mock_formatter.compile_formatter.assert_called_once()

    # Verify the formatter was set to the result of compile_formatter
    assert compiled_handler.formatter == mock_formatter.compile_formatter.return_value


@pytest.mark.unit
@mock.patch("http.client.HTTPConnection")
def test_custom_http_handler_emit_post(mock_http_connection, basic_http_handler):
    """Tests the emit method of the custom HTTP handler with POST method."""
    # Setup mock connection and response
    mock_conn_instance = mock_http_connection.return_value
    mock_response = mock.Mock()
    mock_conn_instance.getresponse.return_value = mock_response

    # Compile the handler and create a log record
    handler = basic_http_handler.compile_handler()
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

    # Verify the connection was created with the correct host
    mock_http_connection.assert_called_with("example.com", timeout=None)

    # Verify the request was made with the correct method, URL, and data
    mock_conn_instance.request.assert_called_once()
    args, kwargs = mock_conn_instance.request.call_args

    # Check method and URL
    assert args[0] == "POST"
    assert args[1] == "/log"

    # Check that the message is in the form data
    assert "message=" in args[2]

    # Verify Content-type header is set for POST
    assert kwargs["headers"]["Content-type"] == "application/x-www-form-urlencoded"

    # Verify the connection was closed
    mock_conn_instance.close.assert_called_once()


@pytest.mark.unit
@mock.patch("http.client.HTTPConnection")
def test_custom_http_handler_emit_get(mock_http_connection, advanced_http_handler):
    """Tests the emit method of the custom HTTP handler with GET method."""
    # Setup mock connection and response
    mock_conn_instance = mock_http_connection.return_value
    mock_response = mock.Mock()
    mock_conn_instance.getresponse.return_value = mock_response

    # Compile the handler and create a log record
    handler = advanced_http_handler.compile_handler()
    record = logging.LogRecord(
        name="test_logger",
        level=logging.DEBUG,
        pathname="",
        lineno=0,
        msg="Test message",
        args=(),
        exc_info=None,
    )

    # Emit the record
    handler.emit(record)

    # Verify the connection was created with the correct host and timeout
    mock_http_connection.assert_called_with("example.com", timeout=5.0)

    # Verify the request was made with the correct method and URL
    mock_conn_instance.request.assert_called_once()
    args, kwargs = mock_conn_instance.request.call_args

    # Check method and that URL contains message parameter
    assert args[0] == "GET"
    assert "/log?message=" in args[1]

    # Verify authorization header is set with credentials
    assert "Authorization" in kwargs["headers"]
    assert kwargs["headers"]["Authorization"].startswith("Basic ")

    # Verify the connection was closed
    mock_conn_instance.close.assert_called_once()


@pytest.mark.unit
@mock.patch("http.client.HTTPConnection")
def test_custom_http_handler_emit_error_handling(
    mock_http_connection, basic_http_handler
):
    """Tests error handling in the emit method."""
    # Setup mock connection to raise an exception
    mock_conn_instance = mock_http_connection.return_value
    mock_conn_instance.request.side_effect = Exception("Test error")

    # Patch handleError method to track calls
    with mock.patch.object(logging.Handler, "handleError") as mock_handle_error:
        # Compile the handler and create a log record
        handler = basic_http_handler.compile_handler()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        # Emit the record (should catch the exception)
        handler.emit(record)

        # Verify handleError was called with the record
        mock_handle_error.assert_called_once_with(record)


@pytest.mark.unit
@pytest.mark.parametrize("method", ["GET", "POST"])
def test_http_handler_with_different_methods(method):
    """Tests HTTP handler with different HTTP methods."""
    handler = HTTPLoggingHandler(host="example.com", url="/log", method=method)
    assert handler.method == method


@pytest.mark.unit
@pytest.mark.parametrize(
    "credentials,expected",
    [
        (None, None),
        (
            {"username": "user", "password": "pass"},
            {"username": "user", "password": "pass"},
        ),
        ({}, {}),
    ],
)
def test_http_handler_with_different_credentials(credentials, expected):
    """Tests HTTP handler with different credential configurations."""
    handler = HTTPLoggingHandler(
        host="example.com", url="/log", credentials=credentials
    )
    assert handler.credentials == expected


@pytest.mark.unit
def test_serialization_deserialization():
    """Tests serialization and deserialization of the handler."""
    # Create a handler with various settings
    original = HTTPLoggingHandler(
        host="example.com",
        url="/log",
        method="GET",
        timeout=5.0,
        credentials={"username": "user", "password": "pass"},
        level=logging.DEBUG,
        formatter="%(levelname)s: %(message)s",
    )

    # Serialize to JSON
    json_data = original.model_dump_json()

    # Deserialize from JSON
    recreated = HTTPLoggingHandler.model_validate_json(json_data)

    # Verify all attributes are preserved
    assert recreated.host == original.host
    assert recreated.url == original.url
    assert recreated.method == original.method
    assert recreated.timeout == original.timeout
    assert recreated.credentials == original.credentials
    assert recreated.level == original.level
    assert recreated.formatter == original.formatter
