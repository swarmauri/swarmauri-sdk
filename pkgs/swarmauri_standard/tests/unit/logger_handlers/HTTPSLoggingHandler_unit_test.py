import logging
import ssl
from unittest.mock import MagicMock, patch

import pytest

from swarmauri_standard.logger_handlers.HTTPSLoggingHandler import HTTPSLoggingHandler


@pytest.fixture
def https_handler():
    """
    Create a basic HTTPSLoggingHandler instance for testing.

    Returns:
        HTTPSLoggingHandler: A configured handler instance.
    """
    return HTTPSLoggingHandler(
        host="test.example.com", url="/logs", port=8443, timeout=2.0
    )


@pytest.mark.unit
def test_type_attribute():
    """Test that the type attribute is correctly set."""
    assert HTTPSLoggingHandler.type == "HTTPSLoggingHandler"


@pytest.mark.unit
def test_init_default_values():
    """Test initialization with default values."""
    handler = HTTPSLoggingHandler()

    assert handler.host == "localhost"
    assert handler.url == "/log"
    assert handler.method == "POST"
    assert handler.port == 443
    assert handler.ssl_context == {}
    assert handler.cert_file is None
    assert handler.key_file is None
    assert handler.ca_certs is None
    assert handler.verify_ssl is True
    assert handler.headers == {"Content-Type": "application/x-www-form-urlencoded"}
    assert handler.timeout == 5.0
    assert handler.additional_params == {}


@pytest.mark.unit
def test_init_custom_values():
    """Test initialization with custom values."""
    custom_headers = {"Content-Type": "application/json", "X-Custom": "Value"}
    custom_params = {"app": "test-app", "env": "testing"}

    handler = HTTPSLoggingHandler(
        level=logging.DEBUG,
        host="logs.example.com",
        url="/api/logs",
        method="PUT",
        port=8443,
        cert_file="/path/to/cert.pem",
        key_file="/path/to/key.pem",
        ca_certs="/path/to/ca.pem",
        verify_ssl=False,
        headers=custom_headers,
        timeout=10.0,
        additional_params=custom_params,
    )

    assert handler.level == logging.DEBUG
    assert handler.host == "logs.example.com"
    assert handler.url == "/api/logs"
    assert handler.method == "PUT"
    assert handler.port == 8443
    assert handler.cert_file == "/path/to/cert.pem"
    assert handler.key_file == "/path/to/key.pem"
    assert handler.ca_certs == "/path/to/ca.pem"
    assert handler.verify_ssl is False
    assert handler.headers == custom_headers
    assert handler.timeout == 10.0
    assert handler.additional_params == custom_params


@pytest.mark.unit
@patch("ssl.create_default_context")
def test_create_ssl_context_default(mock_create_context, https_handler):
    """Test SSL context creation with default settings."""
    mock_context = MagicMock()
    mock_create_context.return_value = mock_context

    context = https_handler._create_ssl_context()

    # Verify context was created with correct purpose
    mock_create_context.assert_called_once_with(purpose=ssl.Purpose.SERVER_AUTH)
    assert context == mock_context
    assert not mock_context.load_cert_chain.called
    assert not mock_context.load_verify_locations.called


@pytest.mark.unit
@patch("ssl.create_default_context")
def test_create_ssl_context_with_client_cert(mock_create_context):
    """Test SSL context creation with client certificate."""
    mock_context = MagicMock()
    mock_create_context.return_value = mock_context

    handler = HTTPSLoggingHandler(
        cert_file="/path/to/cert.pem", key_file="/path/to/key.pem"
    )

    handler._create_ssl_context()

    # Verify context was created with client auth purpose
    mock_create_context.assert_called_once_with(purpose=ssl.Purpose.CLIENT_AUTH)
    # Verify cert chain was loaded
    mock_context.load_cert_chain.assert_called_once_with(
        certfile="/path/to/cert.pem", keyfile="/path/to/key.pem"
    )


@pytest.mark.unit
@patch("ssl.create_default_context")
def test_create_ssl_context_with_ca_certs(mock_create_context):
    """Test SSL context creation with CA certificates."""
    mock_context = MagicMock()
    mock_create_context.return_value = mock_context

    handler = HTTPSLoggingHandler(ca_certs="/path/to/ca.pem")

    handler._create_ssl_context()

    # Verify CA certs were loaded
    mock_context.load_verify_locations.assert_called_once_with(cafile="/path/to/ca.pem")


@pytest.mark.unit
@patch("ssl.create_default_context")
def test_create_ssl_context_no_verify(mock_create_context):
    """Test SSL context creation with verification disabled."""
    mock_context = MagicMock()
    mock_create_context.return_value = mock_context

    handler = HTTPSLoggingHandler(verify_ssl=False)

    handler._create_ssl_context()

    # Verify verification settings were applied
    assert mock_context.check_hostname is False
    assert mock_context.verify_mode == ssl.CERT_NONE


@pytest.mark.unit
@patch("ssl.create_default_context")
def test_create_ssl_context_with_custom_settings(mock_create_context):
    """Test SSL context creation with custom SSL settings."""
    mock_context = MagicMock()
    mock_create_context.return_value = mock_context

    handler = HTTPSLoggingHandler(
        ssl_context={
            "options": ssl.OP_NO_TLSv1,
            "minimum_version": ssl.TLSVersion.TLSv1_2,
        }
    )

    handler._create_ssl_context()

    # Verify custom SSL settings were applied
    assert mock_context.options == ssl.OP_NO_TLSv1
    assert mock_context.minimum_version == ssl.TLSVersion.TLSv1_2


@pytest.mark.unit
def test_format_record_basic(https_handler):
    """Test basic log record formatting."""
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test.py",
        lineno=42,
        msg="Test message",
        args=(),
        exc_info=None,
    )

    formatted_data = https_handler._format_record(record)

    assert "message" in formatted_data
    assert "level" in formatted_data
    assert "logger" in formatted_data
    assert "timestamp" in formatted_data

    assert formatted_data["level"] == "INFO"
    assert formatted_data["logger"] == "test_logger"
    assert "Test message" in formatted_data["message"]


@pytest.mark.unit
def test_format_record_with_exception(https_handler):
    """Test log record formatting with exception information."""
    try:
        raise ValueError("Test exception")
    except ValueError:
        import sys

        exc_info = sys.exc_info()

    record = logging.LogRecord(
        name="test_logger",
        level=logging.ERROR,
        pathname="test.py",
        lineno=42,
        msg="Exception occurred",
        args=(),
        exc_info=exc_info,
    )

    formatted_data = https_handler._format_record(record)

    assert "exception" in formatted_data
    assert "ValueError: Test exception" in formatted_data["exception"]


@pytest.mark.unit
def test_format_record_with_additional_params(https_handler):
    """Test log record formatting with additional parameters."""
    https_handler.additional_params = {"app": "test-app", "env": "testing"}

    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test.py",
        lineno=42,
        msg="Test message",
        args=(),
        exc_info=None,
    )

    formatted_data = https_handler._format_record(record)

    assert formatted_data["app"] == "test-app"
    assert formatted_data["env"] == "testing"


@pytest.mark.unit
@patch("urllib.request.urlopen")
@patch("urllib.request.Request")
def test_send_log_post_request(mock_request, mock_urlopen, https_handler):
    """Test sending a log record via POST request."""
    # Setup mock response
    mock_response = MagicMock()
    mock_response.status = 200
    mock_urlopen.return_value.__enter__.return_value = mock_response

    # Create a log record
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test.py",
        lineno=42,
        msg="Test message",
        args=(),
        exc_info=None,
    )

    # Call the method
    https_handler._send_log(record)

    # Verify request was created correctly
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args

    assert kwargs["url"] == "https://test.example.com:8443/logs"
    assert kwargs["method"] == "POST"
    assert b"message" in kwargs["data"]
    assert kwargs["headers"] == {"Content-Type": "application/x-www-form-urlencoded"}

    # Verify urlopen was called
    mock_urlopen.assert_called_once()


@pytest.mark.unit
@patch("urllib.request.urlopen")
@patch("urllib.request.Request")
def test_send_log_get_request(mock_request, mock_urlopen):
    """Test sending a log record via GET request."""
    # Setup handler with GET method
    handler = HTTPSLoggingHandler(host="test.example.com", url="/logs", method="GET")

    # Setup mock response
    mock_response = MagicMock()
    mock_response.status = 200
    mock_urlopen.return_value.__enter__.return_value = mock_response

    # Create a log record
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test.py",
        lineno=42,
        msg="Test message",
        args=(),
        exc_info=None,
    )

    # Call the method
    handler._send_log(record)

    # Verify request was created correctly
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args

    assert kwargs["url"] == "https://test.example.com:443/logs"
    assert kwargs["method"] == "GET"
    assert kwargs["data"] is None

    # Verify URL parameters were set
    request_instance = mock_request.return_value
    assert "message" in request_instance.full_url
