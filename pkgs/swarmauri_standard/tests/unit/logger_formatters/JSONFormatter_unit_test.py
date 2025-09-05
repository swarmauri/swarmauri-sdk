import datetime
import json
import logging
from unittest.mock import MagicMock, patch

import pytest

from swarmauri_standard.logger_formatters.JSONFormatter import (
    JSONFormatter,
    _JSONLogFormatter,
)


@pytest.fixture
def json_formatter():
    """
    Fixture providing a default JSONFormatter instance.

    Returns
    -------
    JSONFormatter
        A default JSONFormatter instance.
    """
    return JSONFormatter()


@pytest.mark.unit
def test_default_attributes():
    """Test that JSONFormatter has the expected default attributes."""
    formatter = JSONFormatter()
    assert formatter.include_timestamp is True
    assert formatter.include_exception is True
    assert formatter.date_format == "%Y-%m-%dT%H:%M:%S.%fZ"


@pytest.mark.unit
def test_compile_formatter(json_formatter):
    """Test that compile_formatter returns a _JSONLogFormatter instance."""
    formatter = json_formatter.compile_formatter()
    assert isinstance(formatter, _JSONLogFormatter)
    assert formatter.config == json_formatter


@pytest.mark.unit
def test_json_log_formatter_initialization():
    """Test that _JSONLogFormatter initializes correctly with a config."""
    config = JSONFormatter()
    formatter = _JSONLogFormatter(config)
    assert formatter.config == config


@pytest.mark.unit
def test_json_log_formatter_format_basic():
    """Test that _JSONLogFormatter formats a basic log record correctly."""
    config = JSONFormatter()
    formatter = _JSONLogFormatter(config)

    # Create a mock log record
    record = MagicMock(spec=logging.LogRecord)
    record.levelname = "INFO"
    record.name = "test_logger"
    record.getMessage.return_value = "Test message"
    record.created = datetime.datetime.now(tz=datetime.timezone.utc).timestamp()
    record.exc_info = None

    # Format the record
    result = formatter.format(record)

    # Parse the JSON result
    log_data = json.loads(result)

    # Check that the basic fields are correct
    assert log_data["level"] == "INFO"
    assert log_data["name"] == "test_logger"
    assert log_data["message"] == "Test message"
    assert "timestamp" in log_data


@pytest.mark.unit
def test_json_log_formatter_without_timestamp():
    """Test that _JSONLogFormatter can exclude timestamps if configured."""
    config = JSONFormatter(include_timestamp=False)
    formatter = _JSONLogFormatter(config)

    # Create a mock log record
    record = MagicMock(spec=logging.LogRecord)
    record.levelname = "INFO"
    record.name = "test_logger"
    record.getMessage.return_value = "Test message"
    record.created = datetime.datetime.now(tz=datetime.timezone.utc).timestamp()
    record.exc_info = None

    # Format the record
    result = formatter.format(record)

    # Parse the JSON result
    log_data = json.loads(result)

    # Check that timestamp is not included
    assert "timestamp" not in log_data


@pytest.mark.unit
def test_json_log_formatter_with_exception():
    """Test that _JSONLogFormatter includes exception information if present and configured."""
    config = JSONFormatter(include_exception=True)
    formatter = _JSONLogFormatter(config)

    # Create a mock log record with exception info
    record = MagicMock(spec=logging.LogRecord)
    record.levelname = "ERROR"
    record.name = "test_logger"
    record.getMessage.return_value = "Test error message"
    record.created = datetime.datetime.now(tz=datetime.timezone.utc).timestamp()

    # Mock the exception info and formatter method
    record.exc_info = (ValueError, ValueError("Test exception"), None)
    formatter.formatException = MagicMock(return_value="Traceback: Test exception")

    # Format the record
    result = formatter.format(record)

    # Parse the JSON result
    log_data = json.loads(result)

    # Check that exception info is included
    assert "exception" in log_data
    assert log_data["exception"] == "Traceback: Test exception"


@pytest.mark.unit
def test_json_log_formatter_without_exception():
    """Test that _JSONLogFormatter can exclude exception information if configured."""
    config = JSONFormatter(include_exception=False)
    formatter = _JSONLogFormatter(config)

    # Create a mock log record with exception info
    record = MagicMock(spec=logging.LogRecord)
    record.levelname = "ERROR"
    record.name = "test_logger"
    record.getMessage.return_value = "Test error message"
    record.created = datetime.datetime.now(tz=datetime.timezone.utc).timestamp()

    # Mock the exception info
    record.exc_info = (ValueError, ValueError("Test exception"), None)

    # Format the record
    result = formatter.format(record)

    # Parse the JSON result
    log_data = json.loads(result)

    # Check that exception info is not included
    assert "exception" not in log_data


@pytest.mark.unit
def test_json_log_formatter_with_custom_fields():
    """Test that _JSONLogFormatter includes custom fields from the record."""
    config = JSONFormatter()
    formatter = _JSONLogFormatter(config)

    # Create a mock log record with custom fields
    record = MagicMock(spec=logging.LogRecord)
    record.levelname = "INFO"
    record.name = "test_logger"
    record.getMessage.return_value = "Test message"
    record.created = datetime.datetime.now(tz=datetime.timezone.utc).timestamp()
    record.exc_info = None

    # Add custom fields
    record.custom_field = "custom_value"
    record.another_field = 123

    # Format the record
    result = formatter.format(record)

    # Parse the JSON result
    log_data = json.loads(result)

    # Check that custom fields are included
    assert "custom_field" in log_data
    assert log_data["custom_field"] == "custom_value"
    assert "another_field" in log_data
    assert log_data["another_field"] == 123


@pytest.mark.unit
def test_json_log_formatter_with_non_serializable_fields():
    """Test that _JSONLogFormatter handles non-JSON-serializable fields correctly."""
    config = JSONFormatter()
    formatter = _JSONLogFormatter(config)

    # Create a non-serializable object
    class NonSerializable:
        def __str__(self):
            return "Non-serializable object"

    non_serializable = NonSerializable()

    # Create a mock log record with non-serializable field
    record = MagicMock(spec=logging.LogRecord)
    record.levelname = "INFO"
    record.name = "test_logger"
    record.getMessage.return_value = "Test message"
    record.created = datetime.datetime.now(tz=datetime.timezone.utc).timestamp()
    record.exc_info = None

    # Add non-serializable field
    record.non_serializable_field = non_serializable

    # Format the record
    result = formatter.format(record)

    # Parse the JSON result
    log_data = json.loads(result)

    # Check that non-serializable field is converted to string
    assert "non_serializable_field" in log_data
    assert log_data["non_serializable_field"] == "Non-serializable object"


@pytest.mark.unit
def test_json_log_formatter_serialization_failure():
    """Test that _JSONLogFormatter handles serialization failures gracefully."""
    config = JSONFormatter()
    formatter = _JSONLogFormatter(config)

    # Create a mock log record
    record = MagicMock(spec=logging.LogRecord)
    record.levelname = "INFO"
    record.name = "test_logger"
    record.getMessage.return_value = "Test message"
    record.exc_info = None

    # Mock json.dumps to raise an exception
    with patch(
        "json.dumps",
        side_effect=[TypeError("Test serialization error"), '{"fallback": "message"}'],
    ):
        result = formatter.format(record)

    # Since we mocked json.dumps to raise an exception and then return a fallback message,
    # we can't parse the result as JSON. Instead, check that it contains the fallback message.
    assert "fallback" in result


@pytest.mark.unit
@pytest.mark.parametrize(
    "date_format", ["%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M:%S", "%m/%d/%Y %I:%M:%S %p"]
)
def test_json_log_formatter_with_different_date_formats(date_format):
    """Test that _JSONLogFormatter respects different date formats."""
    config = JSONFormatter(date_format=date_format)
    formatter = _JSONLogFormatter(config)

    # Create a mock log record
    record = MagicMock(spec=logging.LogRecord)
    record.levelname = "INFO"
    record.name = "test_logger"
    record.getMessage.return_value = "Test message"
    record.exc_info = None

    # Use a fixed timestamp for predictable testing
    fixed_datetime = datetime.datetime(
        2023, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc
    )
    record.created = fixed_datetime.timestamp()

    # Format the record
    result = formatter.format(record)

    # Parse the JSON result
    log_data = json.loads(result)

    # Check that the timestamp is formatted according to the specified format
    expected_timestamp = fixed_datetime.strftime(date_format)
    assert log_data["timestamp"] == expected_timestamp
