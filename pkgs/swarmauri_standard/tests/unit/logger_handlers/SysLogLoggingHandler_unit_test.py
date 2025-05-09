import logging
import socket
import pytest
from unittest.mock import patch, MagicMock
from logging.handlers import SysLogHandler

from swarmauri_standard.logger_handlers.SysLogLoggingHandler import SysLogLoggingHandler
from swarmauri_base.logger_formatters.FormatterBase import FormatterBase


@pytest.mark.unit
def test_initialization():
    """
    Test initialization of SysLogLoggingHandler with default values.
    """
    handler = SysLogLoggingHandler()
    assert handler.type == "SysLogLoggingHandler"
    assert handler.level == logging.INFO
    assert handler.formatter is None
    assert handler.address == "/dev/log"
    assert handler.facility == "user"
    assert handler.socktype is None


@pytest.mark.unit
def test_get_facility_value():
    """
    Test the _get_facility_value method for converting facility names to values.
    """
    handler = SysLogLoggingHandler()

    # Test with default facility
    assert handler._get_facility_value() == SysLogHandler.LOG_USER

    # Test with a different facility
    handler.facility = "local0"
    assert handler._get_facility_value() == SysLogHandler.LOG_LOCAL0

    # Test with invalid facility
    handler.facility = "invalid_facility"
    with pytest.raises(ValueError) as excinfo:
        handler._get_facility_value()
    assert "Invalid facility" in str(excinfo.value)


@pytest.mark.unit
@pytest.mark.parametrize(
    "address,expected",
    [
        ("/dev/log", "/dev/log"),
        ("localhost:514", ("localhost", 514)),
        (("localhost", 514), ("localhost", 514)),
        ("/var/run/syslog", "/var/run/syslog"),
        ("example.com:1234", ("example.com", 1234)),
        # This should remain a string as port is not an integer
        ("example.com:port", "example.com:port"),
    ],
)
def test_parse_address(address, expected):
    """
    Test the _parse_address method for parsing different address formats.

    Parameters
    ----------
    address : Union[str, Tuple[str, int]]
        The address to parse
    expected : Union[str, Tuple[str, int]]
        The expected parsed result
    """
    handler = SysLogLoggingHandler(address=address)
    assert handler._parse_address() == expected


@pytest.mark.unit
@patch("swarmauri_standard.logger_handlers.SysLogLoggingHandler.SysLogHandler")
def test_compile_handler_with_default_values(mock_syslog_handler):
    """
    Test compile_handler method with default values.
    """
    mock_instance = MagicMock()
    mock_syslog_handler.return_value = mock_instance

    handler = SysLogLoggingHandler()
    result = handler.compile_handler()

    # Verify SysLogHandler was created with correct parameters
    mock_syslog_handler.assert_called_once_with(
        address="/dev/log", facility=SysLogHandler.LOG_USER
    )

    # Verify the handler was configured correctly
    mock_instance.setLevel.assert_called_once_with(logging.INFO)
    mock_instance.setFormatter.assert_called_once()
    assert result == mock_instance


@pytest.mark.unit
@patch("swarmauri_standard.logger_handlers.SysLogLoggingHandler.SysLogHandler")
def test_compile_handler_with_custom_values(mock_syslog_handler):
    """
    Test compile_handler method with custom values.
    """
    mock_instance = MagicMock()
    mock_syslog_handler.return_value = mock_instance

    custom_formatter = "%(levelname)s: %(message)s"
    handler = SysLogLoggingHandler(
        level=logging.ERROR,
        formatter=custom_formatter,
        address=("localhost", 514),
        facility="local0",
        socktype="tcp",
    )
    result = handler.compile_handler()

    # Verify SysLogHandler was created with correct parameters
    mock_syslog_handler.assert_called_once_with(
        address=("localhost", 514),
        facility=SysLogHandler.LOG_LOCAL0,
        socktype=socket.SOCK_STREAM,
    )

    # Verify the handler was configured correctly
    mock_instance.setLevel.assert_called_once_with(logging.ERROR)
    mock_instance.setFormatter.assert_called_once()
    assert result == mock_instance


@pytest.mark.unit
@patch("swarmauri_standard.logger_handlers.SysLogLoggingHandler.SysLogHandler")
def test_compile_handler_with_formatter_object(mock_syslog_handler):
    """
    Test compile_handler method with a formatter object.
    """
    mock_instance = MagicMock()
    mock_syslog_handler.return_value = mock_instance

    # Create a mock formatter
    mock_formatter = MagicMock(spec=FormatterBase)
    mock_formatter_instance = MagicMock()
    mock_formatter.compile_formatter.return_value = mock_formatter_instance

    handler = SysLogLoggingHandler(formatter=mock_formatter)
    result = handler.compile_handler()

    # Verify formatter was used
    mock_formatter.compile_formatter.assert_called_once()
    mock_instance.setFormatter.assert_called_once_with(mock_formatter_instance)
    assert result == mock_instance


@pytest.mark.unit
@patch("swarmauri_standard.logger_handlers.SysLogLoggingHandler.SysLogHandler")
def test_compile_handler_with_invalid_socket_type(mock_syslog_handler):
    """
    Test compile_handler method with an invalid socket type.
    """
    handler = SysLogLoggingHandler(address=("localhost", 514), socktype="invalid")

    with pytest.raises(ValueError) as excinfo:
        handler.compile_handler()

    assert "Invalid socket type" in str(excinfo.value)
    mock_syslog_handler.assert_not_called()


@pytest.mark.unit
@patch("swarmauri_standard.logger_handlers.SysLogLoggingHandler.SysLogHandler")
def test_compile_handler_with_udp_socket(mock_syslog_handler):
    """
    Test compile_handler method with UDP socket.
    """
    mock_instance = MagicMock()
    mock_syslog_handler.return_value = mock_instance

    handler = SysLogLoggingHandler(address=("localhost", 514), socktype="udp")
    result = handler.compile_handler()

    # Verify SysLogHandler was created with correct parameters
    mock_syslog_handler.assert_called_once_with(
        address=("localhost", 514),
        facility=SysLogHandler.LOG_USER,
        socktype=socket.SOCK_DGRAM,
    )
    assert result == mock_instance


@pytest.mark.unit
@patch("swarmauri_standard.logger_handlers.SysLogLoggingHandler.SysLogHandler")
def test_socket_type_ignored_for_unix_socket(mock_syslog_handler):
    """
    Test that socket type is ignored when using a Unix domain socket.
    """
    mock_instance = MagicMock()
    mock_syslog_handler.return_value = mock_instance

    handler = SysLogLoggingHandler(
        address="/dev/log",
        socktype="tcp",  # This should be ignored for Unix socket
    )
    result = handler.compile_handler()

    # Verify SysLogHandler was created with correct parameters
    # Socket type should not be passed for Unix socket
    mock_syslog_handler.assert_called_once_with(
        address="/dev/log", facility=SysLogHandler.LOG_USER
    )
    assert result == mock_instance


@pytest.mark.unit
@patch("swarmauri_standard.logger_handlers.SysLogLoggingHandler.SysLogHandler")
def test_fallback_on_connection_error(mock_syslog_handler):
    """
    Test that a fallback handler is created when a connection error occurs.
    """
    # Make SysLogHandler raise a socket error
    mock_syslog_handler.side_effect = socket.error("Connection refused")

    handler = SysLogLoggingHandler()

    with patch("sys.stderr") as mock_stderr:
        result = handler.compile_handler()

        # Verify a StreamHandler was created as fallback
        assert isinstance(result, logging.StreamHandler)
        assert result.stream == mock_stderr

        # Verify the fallback handler was configured correctly
        assert result.level == logging.INFO
        assert "[SYSLOG ERROR: Connection refused]" in result.formatter._fmt


@pytest.mark.unit
def test_serialization():
    """
    Test serialization and deserialization of SysLogLoggingHandler.
    """
    handler = SysLogLoggingHandler(
        level=logging.DEBUG,
        address=("logserver.example.com", 514),
        facility="local7",
        socktype="tcp",
    )

    # Serialize to JSON
    json_data = handler.model_dump_json()

    # Deserialize from JSON
    deserialized = SysLogLoggingHandler.model_validate_json(json_data)

    # Verify all attributes were preserved
    assert deserialized.level == logging.DEBUG
    assert deserialized.address == ("logserver.example.com", 514)
    assert deserialized.facility == "local7"
    assert deserialized.socktype == "tcp"
