import logging
import os
import tempfile
from datetime import datetime
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest
from swarmauri_base.logger_formatters.FormatterBase import FormatterBase

from swarmauri_standard.logger_handlers.TimedRotatingFileLoggingHandler import (
    TimedRotatingFileLoggingHandler,
)


@pytest.fixture
def temp_log_file() -> Generator[str, None, None]:
    """
    Creates a temporary log file for testing.

    Yields
    ------
    str
        Path to the temporary log file
    """
    with tempfile.NamedTemporaryFile(suffix=".log", delete=False) as tmp:
        log_path = tmp.name

    yield log_path

    # Clean up after the test
    if os.path.exists(log_path):
        os.remove(log_path)


@pytest.fixture
def mock_formatter() -> FormatterBase:
    """Creates a mock formatter for testing."""
    formatter = MagicMock(spec=FormatterBase)
    formatter.type = "FormatterBase"  # Add type attribute for discriminator
    formatter.model_dump = MagicMock(
        return_value={"type": "FormatterBase"}
    )  # For Pydantic serialization
    formatter.compile_formatter.return_value = logging.Formatter("[TEST] %(message)s")
    return formatter


@pytest.mark.unit
def test_init_default_values():
    """Tests that the handler initializes with correct default values."""
    handler = TimedRotatingFileLoggingHandler(filename="/tmp/test.log")

    assert handler.type == "TimedRotatingFileLoggingHandler"
    assert handler.filename == "/tmp/test.log"
    assert handler.when == "midnight"
    assert handler.interval == 1
    assert handler.backupCount == 7
    assert handler.encoding is None
    assert handler.delay is False
    assert handler.utc is False
    assert handler.atTime is None
    assert handler.level == logging.INFO
    assert handler.formatter is None


@pytest.mark.unit
def test_init_custom_values():
    """Tests that the handler initializes with custom values."""
    custom_time = datetime.now()
    handler = TimedRotatingFileLoggingHandler(
        filename="/tmp/custom.log",
        when="H",
        interval=2,
        backupCount=10,
        encoding="utf-8",
        delay=True,
        utc=True,
        atTime=custom_time,
        level=logging.DEBUG,
        formatter="[%(levelname)s] %(message)s",
    )

    assert handler.type == "TimedRotatingFileLoggingHandler"
    assert handler.filename == "/tmp/custom.log"
    assert handler.when == "H"
    assert handler.interval == 2
    assert handler.backupCount == 10
    assert handler.encoding == "utf-8"
    assert handler.delay is True
    assert handler.utc is True
    assert handler.atTime == custom_time
    assert handler.level == logging.DEBUG
    assert handler.formatter == "[%(levelname)s] %(message)s"


@pytest.mark.unit
def test_compile_handler_with_string_formatter(temp_log_file):
    """Tests that compile_handler correctly creates a handler with a string formatter."""
    handler_config = TimedRotatingFileLoggingHandler(
        filename=temp_log_file, formatter="[%(levelname)s] %(message)s"
    )

    log_handler = handler_config.compile_handler()

    assert isinstance(log_handler, logging.handlers.TimedRotatingFileHandler)
    assert log_handler.level == logging.INFO
    assert log_handler.formatter._fmt == "[%(levelname)s] %(message)s"
    assert log_handler.baseFilename == temp_log_file


@pytest.mark.unit
def test_compile_handler_with_formatter_object(temp_log_file, mock_formatter):
    """Tests that compile_handler correctly creates a handler with a formatter object."""
    handler_config = TimedRotatingFileLoggingHandler(
        filename=temp_log_file, formatter=mock_formatter
    )

    log_handler = handler_config.compile_handler()

    assert isinstance(log_handler, logging.handlers.TimedRotatingFileHandler)
    assert log_handler.formatter._fmt == "[TEST] %(message)s"
    mock_formatter.compile_formatter.assert_called_once()


@pytest.mark.unit
def test_compile_handler_without_formatter(temp_log_file):
    """Tests that compile_handler correctly creates a handler with the default formatter."""
    handler_config = TimedRotatingFileLoggingHandler(filename=temp_log_file)

    log_handler = handler_config.compile_handler()

    assert isinstance(log_handler, logging.handlers.TimedRotatingFileHandler)
    assert (
        log_handler.formatter._fmt
        == "[%(asctime)s][%(name)s][%(levelname)s] %(message)s"
    )


@pytest.mark.unit
def test_get_handler_config():
    """Tests that get_handler_config returns the correct configuration dictionary."""
    custom_time = datetime.now()
    formatter = "[%(levelname)s] %(message)s"

    handler = TimedRotatingFileLoggingHandler(
        filename="/tmp/config_test.log",
        when="D",
        interval=3,
        backupCount=5,
        encoding="utf-8",
        delay=True,
        utc=True,
        atTime=custom_time,
        level=logging.WARNING,
        formatter=formatter,
    )

    config = handler.get_handler_config()

    assert config["type"] == "TimedRotatingFileLoggingHandler"
    assert config["filename"] == "/tmp/config_test.log"
    assert config["when"] == "D"
    assert config["interval"] == 3
    assert config["backupCount"] == 5
    assert config["encoding"] == "utf-8"
    assert config["delay"] is True
    assert config["utc"] is True
    assert config["atTime"] == custom_time
    assert config["level"] == logging.WARNING
    assert config["formatter"] == formatter


@pytest.mark.unit
@patch(
    "swarmauri_standard.logger_handlers.TimedRotatingFileLoggingHandler.TimedRotatingFileHandler"
)
def test_handler_initialization_parameters(mock_handler_class, temp_log_file):
    """Tests that the TimedRotatingFileHandler is initialized with the correct parameters."""
    custom_time = datetime.now()

    handler_config = TimedRotatingFileLoggingHandler(
        filename=temp_log_file,
        when="W0",
        interval=2,
        backupCount=3,
        encoding="utf-8",
        delay=True,
        utc=True,
        atTime=custom_time,
    )

    handler_config.compile_handler()

    # Verify the TimedRotatingFileHandler was created with correct parameters
    mock_handler_class.assert_called_once_with(
        filename=temp_log_file,
        when="W0",
        interval=2,
        backupCount=3,
        encoding="utf-8",
        delay=True,
        utc=True,
        atTime=custom_time,
    )


@pytest.mark.unit
@pytest.mark.parametrize(
    "when,interval,expected_seconds",
    [
        ("S", 60, 60),  # 60 seconds
        ("M", 30, 30 * 60),  # 30 minutes = 1800 seconds
        ("H", 12, 12 * 3600),  # 12 hours = 43200 seconds
        ("D", 1, 86400),  # 1 day = 86400 seconds
        ("W0", 1, 604800),  # 1 week = 604800 seconds
        ("midnight", 1, 86400),  # 1 day = 86400 seconds
    ],
)
def test_various_rotation_configurations(
    when, interval, expected_seconds, temp_log_file
):
    """Tests that various rotation configurations are properly set."""
    handler_config = TimedRotatingFileLoggingHandler(
        filename=temp_log_file, when=when, interval=interval
    )

    log_handler = handler_config.compile_handler()

    assert log_handler.when.lower() == when.lower()
    assert log_handler.interval == expected_seconds


@pytest.mark.unit
def test_functional_logging(temp_log_file):
    """Tests that the handler works functionally for logging messages."""
    # Create and configure the handler
    handler_config = TimedRotatingFileLoggingHandler(
        filename=temp_log_file, level=logging.DEBUG
    )

    # Set up a logger
    logger = logging.getLogger("test_logger")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler_config.compile_handler())

    # Log a test message
    test_message = "This is a test log message"
    logger.debug(test_message)

    # Verify the message was written to the file
    with open(temp_log_file, "r") as f:
        log_content = f.read()

    assert test_message in log_content


@pytest.mark.unit
def test_model_serialization_deserialization():
    """Tests that the model can be properly serialized and deserialized."""
    original = TimedRotatingFileLoggingHandler(
        filename="/tmp/serialization_test.log",
        when="H",
        interval=4,
        backupCount=10,
        level=logging.ERROR,
    )

    # Serialize to JSON
    json_data = original.model_dump_json()

    # Deserialize from JSON
    deserialized = TimedRotatingFileLoggingHandler.model_validate_json(json_data)

    # Verify properties match
    assert deserialized.filename == original.filename
    assert deserialized.when == original.when
    assert deserialized.interval == original.interval
    assert deserialized.backupCount == original.backupCount
    assert deserialized.level == original.level
