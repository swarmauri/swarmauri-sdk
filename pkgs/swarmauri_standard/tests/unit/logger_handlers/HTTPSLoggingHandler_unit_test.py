import json
import logging
import ssl
from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest

from swarmauri_standard.logger_handlers.HTTPSLoggingHandler import (
    HTTPSLoggingHandler,
    _HTTPSHandler,
)


@pytest.fixture
def handler_config() -> Dict[str, Any]:
    """
    Fixture providing a standard configuration for HTTPSLoggingHandler.

    Returns:
        Dict[str, Any]: A dictionary with configuration parameters.
    """
    return {
        "host": "example.com",
        "url": "/logs",
        "method": "POST",
        "port": 443,
        "verify_ssl": True,
        "timeout": 5,
        "headers": {"Content-Type": "application/json", "X-Api-Key": "test-key"},
        "level": logging.INFO,
    }


@pytest.fixture
def https_handler(handler_config) -> HTTPSLoggingHandler:
    """
    Fixture providing an instance of HTTPSLoggingHandler.

    Args:
        handler_config: Configuration parameters for the handler.

    Returns:
        HTTPSLoggingHandler: An instance of the handler.
    """
    return HTTPSLoggingHandler(**handler_config)


@pytest.mark.unit
def test_https_handler_initialization(https_handler):
    """
    Test that HTTPSLoggingHandler initializes with correct attributes.

    Args:
        https_handler: The handler instance.
    """
    assert https_handler.type == "HTTPSLoggingHandler"
    assert https_handler.host == "example.com"
    assert https_handler.url == "/logs"
    assert https_handler.method == "POST"
    assert https_handler.port == 443
    assert https_handler.verify_ssl is True
    assert https_handler.timeout == 5
    assert https_handler.headers == {
        "Content-Type": "application/json",
        "X-Api-Key": "test-key",
    }
    assert https_handler.level == logging.INFO


@pytest.mark.unit
def test_https_handler_default_values():
    """Test that HTTPSLoggingHandler uses correct default values."""
    handler = HTTPSLoggingHandler(host="example.com", url="/logs")

    assert handler.method == "POST"
    assert handler.port == 443
    assert handler.verify_ssl is True
    assert handler.timeout == 5
    assert handler.headers == {"Content-Type": "application/json"}
    assert handler.ssl_context is None
    assert handler.cert_file is None
    assert handler.key_file is None


@pytest.mark.unit
def test_compile_handler_returns_logging_handler(https_handler):
    """
    Test that compile_handler returns a logging.Handler instance.

    Args:
        https_handler: The handler instance.
    """
    handler = https_handler.compile_handler()
    assert isinstance(handler, logging.Handler)
    assert isinstance(handler, _HTTPSHandler)


@pytest.mark.unit
def test_compile_handler_sets_level(https_handler):
    """
    Test that compile_handler sets the correct log level.

    Args:
        https_handler: The handler instance.
    """
    https_handler.level = logging.DEBUG
    handler = https_handler.compile_handler()
    assert handler.level == logging.DEBUG

    https_handler.level = logging.ERROR
    handler = https_handler.compile_handler()
    assert handler.level == logging.ERROR


@pytest.mark.unit
def test_compile_handler_with_string_formatter(https_handler):
    """
    Test that compile_handler correctly configures a string formatter.

    Args:
        https_handler: The handler instance.
    """
    format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    https_handler.formatter = format_string

    handler = https_handler.compile_handler()

    assert isinstance(handler.formatter, logging.Formatter)
    assert handler.formatter._fmt == format_string


@pytest.mark.unit
def test_compile_handler_with_default_formatter(https_handler):
    """
    Test that compile_handler uses a default formatter when none is provided.

    Args:
        https_handler: The handler instance.
    """
    https_handler.formatter = None
    handler = https_handler.compile_handler()

    assert isinstance(handler.formatter, logging.Formatter)
    assert handler.formatter._fmt == "[%(name)s][%(levelname)s] %(message)s"


@pytest.mark.unit
@patch(
    "swarmauri_standard.logger_handlers.HTTPSLoggingHandler.ssl.create_default_context"
)
def test_https_handler_create_ssl_context(mock_create_context, https_handler):
    """
    Test the SSL context creation in _HTTPSHandler.

    Args:
        mock_create_context: Mocked ssl.create_default_context function.
        https_handler: The handler instance.
    """
    mock_context = MagicMock()
    mock_create_context.return_value = mock_context

    handler = https_handler.compile_handler()
    ssl_context = handler._create_ssl_context()

    assert ssl_context == mock_context
    mock_create_context.assert_called_once()


@pytest.mark.unit
@patch(
    "swarmauri_standard.logger_handlers.HTTPSLoggingHandler.ssl.create_default_context"
)
def test_https_handler_ssl_verification_disabled(mock_create_context):
    """
    Test that SSL verification can be disabled.

    Args:
        mock_create_context: Mocked ssl.create_default_context function.
    """
    mock_context = MagicMock()
    mock_create_context.return_value = mock_context

    handler_config = {"host": "example.com", "url": "/logs", "verify_ssl": False}

    handler = HTTPSLoggingHandler(**handler_config).compile_handler()
    handler._create_ssl_context()

    assert mock_context.check_hostname is False
    assert mock_context.verify_mode == ssl.CERT_NONE


@pytest.mark.unit
@patch(
    "swarmauri_standard.logger_handlers.HTTPSLoggingHandler.ssl.create_default_context"
)
def test_https_handler_with_client_certificates(mock_create_context):
    """
    Test that client certificates are correctly loaded.

    Args:
        mock_create_context: Mocked ssl.create_default_context function.
    """
    mock_context = MagicMock()
    mock_create_context.return_value = mock_context

    handler_config = {
        "host": "example.com",
        "url": "/logs",
        "cert_file": "/path/to/cert.pem",
        "key_file": "/path/to/key.pem",
    }

    handler = HTTPSLoggingHandler(**handler_config).compile_handler()
    handler._create_ssl_context()

    mock_context.load_cert_chain.assert_called_once_with(
        certfile="/path/to/cert.pem", keyfile="/path/to/key.pem"
    )


@pytest.mark.unit
@patch(
    "swarmauri_standard.logger_handlers.HTTPSLoggingHandler.ssl.create_default_context"
)
def test_https_handler_with_custom_ssl_context(mock_create_context):
    """
    Test that custom SSL context parameters are applied.

    Args:
        mock_create_context: Mocked ssl.create_default_context function.
    """
    mock_context = MagicMock()
    mock_create_context.return_value = mock_context

    # Set attributes that exist on SSLContext
    mock_context.protocol = None
    mock_context.options = None

    handler_config = {
        "host": "example.com",
        "url": "/logs",
        "ssl_context": {
            "protocol": ssl.PROTOCOL_TLS_CLIENT,
            "options": ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1,
        },
    }

    handler = HTTPSLoggingHandler(**handler_config).compile_handler()
    handler._create_ssl_context()

    assert mock_context.protocol == ssl.PROTOCOL_TLS_CLIENT
    assert mock_context.options == ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1


@pytest.mark.unit
@patch(
    "swarmauri_standard.logger_handlers.HTTPSLoggingHandler.http.client.HTTPSConnection"
)
def test_https_handler_emit(mock_https_connection, https_handler):
    """
    Test the emit method of _HTTPSHandler.

    Args:
        mock_https_connection: Mocked HTTPSConnection class.
        https_handler: The handler instance.
    """
    # Setup mocks
    mock_connection = MagicMock()
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.reason = "OK"

    mock_connection.getresponse.return_value = mock_response
    mock_https_connection.return_value = mock_connection

    # Create a log record
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="Test log message",
        args=(),
        exc_info=None,
    )

    # Create the handler and emit the record
    handler = https_handler.compile_handler()
    with patch.object(handler, "_create_ssl_context") as mock_create_context:
        mock_ssl_context = MagicMock()
        mock_create_context.return_value = mock_ssl_context
        handler.emit(record)

    # Verify the HTTP connection was created correctly
    mock_https_connection.assert_called_once_with(
        host="example.com", port=443, context=mock_ssl_context, timeout=5
    )

    # Verify the request was made with the correct parameters
    mock_connection.request.assert_called_once()
    method, url, body, headers = mock_connection.request.call_args[1].values()

    assert method == "POST"
    assert url == "/logs"
    assert isinstance(body, bytes)
    assert headers == {"Content-Type": "application/json", "X-Api-Key": "test-key"}

    # Check payload content
    payload = json.loads(body.decode("utf-8"))
    assert "message" in payload
    assert payload["level"] == "INFO"
    assert payload["logger"] == "test_logger"
    assert "timestamp" in payload


@pytest.mark.unit
@patch(
    "swarmauri_standard.logger_handlers.HTTPSLoggingHandler.http.client.HTTPSConnection"
)
@patch("swarmauri_standard.logger_handlers.HTTPSLoggingHandler.logging.getLogger")
def test_https_handler_emit_with_failed_response(
    mock_get_logger, mock_https_connection, https_handler
):
    """
    Test the emit method when the server returns an error.

    Args:
        mock_get_logger: Mocked logging.getLogger function.
        mock_https_connection: Mocked HTTPSConnection class.
        https_handler: The handler instance.
    """
    # Setup mocks
    mock_connection = MagicMock()
    mock_response = MagicMock()
    mock_response.status = 500
    mock_response.reason = "Internal Server Error"

    mock_connection.getresponse.return_value = mock_response
    mock_https_connection.return_value = mock_connection

    mock_logger = MagicMock()
    mock_get_logger.return_value = mock_logger

    # Create a log record
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="Test log message",
        args=(),
        exc_info=None,
    )

    # Create the handler and emit the record
    handler = https_handler.compile_handler()
    with patch.object(handler, "_create_ssl_context"):
        handler.emit(record)

    # Verify warning was logged
    mock_get_logger.assert_called_with("HTTPSLoggingHandler")
    mock_logger.warning.assert_called_with(
        "Failed to send log record: HTTP 500 - Internal Server Error"
    )


@pytest.mark.unit
@patch(
    "swarmauri_standard.logger_handlers.HTTPSLoggingHandler.http.client.HTTPSConnection"
)
@patch("swarmauri_standard.logger_handlers.HTTPSLoggingHandler.logging.getLogger")
def test_https_handler_emit_with_exception(
    mock_get_logger, mock_https_connection, https_handler
):
    """
    Test the emit method when an exception occurs.

    Args:
        mock_get_logger: Mocked logging.getLogger function.
        mock_https_connection: Mocked HTTPSConnection class.
        https_handler: The handler instance.
    """
    # Setup mocks
    mock_https_connection.side_effect = Exception("Connection error")

    mock_logger = MagicMock()
    mock_get_logger.return_value = mock_logger

    # Create a log record
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="Test log message",
        args=(),
        exc_info=None,
    )

    # Create the handler and emit the record
    handler = https_handler.compile_handler()
    with patch.object(handler, "handleError") as mock_handle_error:
        with patch.object(handler, "_create_ssl_context"):
            handler.emit(record)

    # Verify error handling
    mock_handle_error.assert_called_once_with(record)
    mock_get_logger.assert_called_with("HTTPSLoggingHandler")
    mock_logger.error.assert_called_with("Error sending log record: Connection error")


@pytest.mark.unit
def test_https_handler_emit_with_extra_attributes(https_handler):
    """
    Test that extra attributes in the log record are included in the payload.

    Args:
        https_handler: The handler instance.
    """
    # Create a log record with extra attributes
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="Test log message",
        args=(),
        exc_info=None,
    )
    record.extra = {
        "user_id": "12345",
        "request_id": "abc-123",
        "application": "test_app",
    }

    # Create the handler
    handler = https_handler.compile_handler()

    # Mock the connection and capture the payload
    with patch(
        "swarmauri_standard.logger_handlers.HTTPSLoggingHandler.http.client.HTTPSConnection"
    ) as mock_conn:
        mock_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.status = 200
        mock_instance.getresponse.return_value = mock_response
        mock_conn.return_value = mock_instance

        with patch.object(handler, "_create_ssl_context"):
            handler.emit(record)

        # Get the payload from the request call
        body = mock_instance.request.call_args[1]["body"]
        payload = json.loads(body.decode("utf-8"))

        # Verify extra attributes are included
        assert payload["user_id"] == "12345"
        assert payload["request_id"] == "abc-123"
        assert payload["application"] == "test_app"
