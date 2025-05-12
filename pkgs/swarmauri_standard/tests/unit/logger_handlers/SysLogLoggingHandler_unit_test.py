import logging
import socket
import unittest.mock as mock
from logging.handlers import SysLogHandler

import pytest
from swarmauri_base.logger_formatters.FormatterBase import FormatterBase

from swarmauri_standard.logger_handlers.SysLogLoggingHandler import SysLogLoggingHandler


@pytest.fixture
def default_handler():
    """
    Creates a default SysLogLoggingHandler instance for testing.

    Returns:
        SysLogLoggingHandler: A default instance of the handler
    """
    return SysLogLoggingHandler()


@pytest.fixture
def custom_handler():
    """
    Creates a customized SysLogLoggingHandler instance for testing.

    Returns:
        SysLogLoggingHandler: A customized instance of the handler
    """
    return SysLogLoggingHandler(
        address=("192.168.1.1", 514),
        facility=SysLogHandler.LOG_LOCAL0,
        socktype=socket.SOCK_STREAM,
        level=logging.WARNING,
    )


@pytest.mark.unit
def test_type():
    """Tests if the handler type is correctly set."""
    # Change from class attribute access to instance attribute access
    handler = SysLogLoggingHandler()
    assert handler.type == "SysLogLoggingHandler"


@pytest.mark.unit
def test_default_attributes(default_handler):
    """Tests if default attributes are correctly set."""
    assert default_handler.address == ("localhost", 514)
    assert default_handler.facility == SysLogHandler.LOG_USER
    assert default_handler.socktype == socket.SOCK_DGRAM
    assert default_handler.formatter is None
    assert default_handler.level == logging.INFO


@pytest.mark.unit
def test_custom_attributes(custom_handler):
    """Tests if custom attributes are correctly set."""
    assert custom_handler.address == ("192.168.1.1", 514)
    assert custom_handler.facility == SysLogHandler.LOG_LOCAL0
    assert custom_handler.socktype == socket.SOCK_STREAM
    assert custom_handler.level == logging.WARNING


@pytest.mark.unit
def test_compile_handler_with_default_settings(default_handler):
    """Tests compiling handler with default settings."""
    with mock.patch(
        "swarmauri_standard.logger_handlers.SysLogLoggingHandler.SysLogHandler"
    ) as mock_handler:
        # Set up the mock
        mock_instance = mock_handler.return_value

        # Call the method
        handler = default_handler.compile_handler()

        # Verify SysLogHandler was called with correct parameters
        mock_handler.assert_called_once_with(
            address=("localhost", 514),
            facility=SysLogHandler.LOG_USER,
            socktype=socket.SOCK_DGRAM,
        )

        # Verify level was set
        mock_instance.setLevel.assert_called_once_with(logging.INFO)

        # Verify formatter was set (default formatter)
        assert mock_instance.setFormatter.called

        # Ensure the handler is returned
        assert handler == mock_instance


@pytest.mark.unit
def test_compile_handler_with_custom_settings(custom_handler):
    """Tests compiling handler with custom settings."""
    with mock.patch(
        "swarmauri_standard.logger_handlers.SysLogLoggingHandler.SysLogHandler"
    ) as mock_handler:
        # Set up the mock
        mock_instance = mock_handler.return_value

        # Call the method
        handler = custom_handler.compile_handler()

        # Verify SysLogHandler was called with correct parameters
        mock_handler.assert_called_once_with(
            address=("192.168.1.1", 514),
            facility=SysLogHandler.LOG_LOCAL0,
            socktype=socket.SOCK_STREAM,
        )

        # Verify level was set
        mock_instance.setLevel.assert_called_once_with(logging.WARNING)

        # Verify formatter was set (default formatter)
        assert mock_instance.setFormatter.called

        # Ensure the handler is returned
        assert handler == mock_instance


@pytest.mark.unit
def test_compile_handler_with_string_formatter():
    """Tests compiling handler with a string formatter."""
    handler_with_string_fmt = SysLogLoggingHandler(
        formatter="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    with (
        mock.patch(
            "swarmauri_standard.logger_handlers.SysLogLoggingHandler.SysLogHandler"
        ) as mock_handler,
        mock.patch("logging.Formatter") as mock_formatter,
    ):
        # Set up the mocks
        mock_instance = mock_handler.return_value
        mock_fmt_instance = mock_formatter.return_value

        # Call the method
        handler_with_string_fmt.compile_handler()

        # Verify formatter was created with correct format string
        mock_formatter.assert_called_once_with(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        # Verify formatter was set on handler
        mock_instance.setFormatter.assert_called_once_with(mock_fmt_instance)


@pytest.mark.unit
def test_compile_handler_with_formatter_object():
    """Tests compiling handler with a FormatterBase object."""
    # Create a mock formatter
    mock_formatter = mock.MagicMock(spec=FormatterBase)
    mock_formatter.type = "FormatterBase"  # Add this for discriminator
    mock_formatter.compile_formatter.return_value = mock.MagicMock()

    handler_with_obj_fmt = SysLogLoggingHandler(formatter=mock_formatter)

    with mock.patch(
        "swarmauri_standard.logger_handlers.SysLogLoggingHandler.SysLogHandler"
    ) as mock_handler:
        # Set up the mock
        mock_instance = mock_handler.return_value

        # Call the method
        handler_with_obj_fmt.compile_handler()

        # Verify formatter's compile_formatter was called
        mock_formatter.compile_formatter.assert_called_once()

        # Verify formatter was set on handler
        mock_instance.setFormatter.assert_called_once_with(
            mock_formatter.compile_formatter.return_value
        )


@pytest.mark.unit
def test_compile_handler_socket_error():
    """Tests handling of socket errors during compilation."""
    handler = SysLogLoggingHandler()

    with (
        mock.patch(
            "swarmauri_standard.logger_handlers.SysLogLoggingHandler.SysLogHandler",
            side_effect=socket.error("Connection refused"),
        ),
        mock.patch("logging.error") as mock_log_error,
        mock.patch("logging.NullHandler") as mock_null_handler,
    ):
        # Set up the mock
        mock_null_instance = mock_null_handler.return_value

        # Call the method
        result = handler.compile_handler()

        # Verify error was logged
        mock_log_error.assert_called_once()
        assert "Failed to connect to syslog server" in mock_log_error.call_args[0][0]

        # Verify NullHandler was returned
        mock_null_handler.assert_called_once()
        assert result == mock_null_instance


@pytest.mark.unit
def test_compile_handler_general_exception():
    """Tests handling of general exceptions during compilation."""
    handler = SysLogLoggingHandler()

    with (
        mock.patch(
            "swarmauri_standard.logger_handlers.SysLogLoggingHandler.SysLogHandler",
            side_effect=Exception("Unexpected error"),
        ),
        mock.patch("logging.error") as mock_log_error,
        mock.patch("logging.NullHandler") as mock_null_handler,
    ):
        # Set up the mock
        mock_null_instance = mock_null_handler.return_value

        # Call the method
        result = handler.compile_handler()

        # Verify error was logged
        mock_log_error.assert_called_once()
        assert "Error setting up SysLogHandler" in mock_log_error.call_args[0][0]

        # Verify NullHandler was returned
        mock_null_handler.assert_called_once()
        assert result == mock_null_instance


@pytest.mark.unit
@pytest.mark.parametrize(
    "address,expected",
    [
        (
            ("localhost", 514),
            "SysLogLoggingHandler(address=localhost:514, facility=1, level=INFO)",  # Change NOTSET to INFO
        ),
        (
            ("/dev/log",),
            "SysLogLoggingHandler(address=/dev/log, facility=1, level=INFO)",  # Change NOTSET to INFO
        ),
    ],
)
def test_str_representation(address, expected):
    """Tests string representation of the handler with different address types."""
    if len(address) == 1:
        handler = SysLogLoggingHandler(address=address[0])
    else:
        handler = SysLogLoggingHandler(address=address)

    assert str(handler) == expected


@pytest.mark.unit
def test_model_serialization():
    """Tests serialization and deserialization of the handler."""
    # Create an instance with custom values
    original = SysLogLoggingHandler(
        address=("remote-server.example.com", 10514),
        facility=SysLogHandler.LOG_LOCAL7,
        socktype=socket.SOCK_STREAM,
        level=logging.INFO,
    )

    # Serialize to JSON
    json_data = original.model_dump_json()

    # Deserialize from JSON
    recreated = SysLogLoggingHandler.model_validate_json(json_data)

    # Verify all properties match
    assert recreated.address == original.address
    assert recreated.facility == original.facility
    assert recreated.socktype == original.socktype
    assert recreated.level == original.level
    assert recreated.type == original.type
