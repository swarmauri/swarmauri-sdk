import os
import pytest
import tempfile
import logging
from datetime import datetime
from unittest.mock import MagicMock, patch

from swarmauri_standard.logger_handlers.TimedRotatingFileLoggingHandler import (
    TimedRotatingFileLoggingHandler,
)
from swarmauri_base.logger_formatters.FormatterBase import FormatterBase


@pytest.fixture
def temp_log_dir():
    """
    Creates a temporary directory for log files.

    Returns
    -------
    str
        Path to the temporary directory.
    """
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield tmpdirname


@pytest.mark.unit
def test_type():
    """
    Tests if the type attribute is correctly set.
    """
    assert TimedRotatingFileLoggingHandler.type == "TimedRotatingFileLoggingHandler"


@pytest.mark.unit
def test_default_values():
    """
    Tests if default values are correctly set.
    """
    handler = TimedRotatingFileLoggingHandler()
    assert handler.level == logging.INFO
    assert handler.filename == "app.log"
    assert handler.when == "midnight"
    assert handler.interval == 1
    assert handler.backupCount == 7
    assert handler.encoding is None
    assert handler.delay is False
    assert handler.utc is False
    assert handler.atTime is None


@pytest.mark.unit
def test_custom_values():
    """
    Tests if custom values are correctly set.
    """
    handler = TimedRotatingFileLoggingHandler(
        level=logging.DEBUG,
        filename="custom.log",
        when="H",
        interval=2,
        backupCount=10,
        encoding="utf-8",
        delay=True,
        utc=True,
    )

    assert handler.level == logging.DEBUG
    assert handler.filename == "custom.log"
    assert handler.when == "H"
    assert handler.interval == 2
    assert handler.backupCount == 10
    assert handler.encoding == "utf-8"
    assert handler.delay is True
    assert handler.utc is True


@pytest.mark.unit
def test_compile_handler_creates_directory(temp_log_dir):
    """
    Tests if the compile_handler method creates the directory for the log file.

    Parameters
    ----------
    temp_log_dir : str
        Path to a temporary directory.
    """
    log_subdir = os.path.join(temp_log_dir, "logs")
    log_file = os.path.join(log_subdir, "test.log")

    handler = TimedRotatingFileLoggingHandler(filename=log_file)

    # Directory should not exist yet
    assert not os.path.exists(log_subdir)

    # Compile the handler
    compiled_handler = handler.compile_handler()

    # Directory should now exist
    assert os.path.exists(log_subdir)

    # Cleanup
    compiled_handler.close()


@pytest.mark.unit
def test_compile_handler_returns_correct_type():
    """
    Tests if compile_handler returns a TimedRotatingFileHandler.
    """
    handler = TimedRotatingFileLoggingHandler()
    compiled_handler = handler.compile_handler()

    assert isinstance(compiled_handler, logging.handlers.TimedRotatingFileHandler)

    # Cleanup
    compiled_handler.close()


@pytest.mark.unit
def test_compile_handler_sets_level():
    """
    Tests if compile_handler sets the correct logging level.
    """
    handler = TimedRotatingFileLoggingHandler(level=logging.WARNING)
    compiled_handler = handler.compile_handler()

    assert compiled_handler.level == logging.WARNING

    # Cleanup
    compiled_handler.close()


@pytest.mark.unit
def test_compile_handler_with_string_formatter():
    """
    Tests if compile_handler correctly handles string formatters.
    """
    format_string = "%(levelname)s - %(message)s"
    handler = TimedRotatingFileLoggingHandler(formatter=format_string)
    compiled_handler = handler.compile_handler()

    assert isinstance(compiled_handler.formatter, logging.Formatter)
    assert compiled_handler.formatter._fmt == format_string

    # Cleanup
    compiled_handler.close()


@pytest.mark.unit
def test_compile_handler_with_formatter_object():
    """
    Tests if compile_handler correctly handles FormatterBase objects.
    """
    mock_formatter = MagicMock(spec=FormatterBase)
    mock_formatter.compile_formatter.return_value = logging.Formatter("%(message)s")

    handler = TimedRotatingFileLoggingHandler(formatter=mock_formatter)
    compiled_handler = handler.compile_handler()

    # Check if the formatter's compile_formatter method was called
    mock_formatter.compile_formatter.assert_called_once()

    # Cleanup
    compiled_handler.close()


@pytest.mark.unit
def test_compile_handler_with_default_formatter():
    """
    Tests if compile_handler uses a default formatter when none is specified.
    """
    handler = TimedRotatingFileLoggingHandler(formatter=None)
    compiled_handler = handler.compile_handler()

    assert isinstance(compiled_handler.formatter, logging.Formatter)
    assert (
        "[%(asctime)s][%(name)s][%(levelname)s] %(message)s"
        in compiled_handler.formatter._fmt
    )

    # Cleanup
    compiled_handler.close()


@pytest.mark.unit
@patch("logging.handlers.TimedRotatingFileHandler")
def test_compile_handler_passes_correct_parameters(mock_handler_class):
    """
    Tests if compile_handler passes the correct parameters to TimedRotatingFileHandler.

    Parameters
    ----------
    mock_handler_class : MagicMock
        Mock for the TimedRotatingFileHandler class.
    """
    handler = TimedRotatingFileLoggingHandler(
        filename="test.log",
        when="H",
        interval=2,
        backupCount=10,
        encoding="utf-8",
        delay=True,
        utc=True,
        atTime=datetime(2023, 1, 1, 12, 0).time(),
    )

    handler.compile_handler()

    # Check if TimedRotatingFileHandler was called with the correct parameters
    mock_handler_class.assert_called_once_with(
        filename="test.log",
        when="H",
        interval=2,
        backupCount=10,
        encoding="utf-8",
        delay=True,
        utc=True,
        atTime=datetime(2023, 1, 1, 12, 0).time(),
    )


@pytest.mark.unit
def test_serialization_deserialization():
    """
    Tests serialization and deserialization of the handler.
    """
    original_handler = TimedRotatingFileLoggingHandler(
        level=logging.DEBUG,
        filename="custom.log",
        when="H",
        interval=2,
        backupCount=10,
        encoding="utf-8",
        delay=True,
        utc=True,
    )

    # Serialize to JSON
    json_data = original_handler.model_dump_json()

    # Deserialize from JSON
    deserialized_handler = TimedRotatingFileLoggingHandler.model_validate_json(
        json_data
    )

    # Check if all attributes match
    assert deserialized_handler.level == original_handler.level
    assert deserialized_handler.filename == original_handler.filename
    assert deserialized_handler.when == original_handler.when
    assert deserialized_handler.interval == original_handler.interval
    assert deserialized_handler.backupCount == original_handler.backupCount
    assert deserialized_handler.encoding == original_handler.encoding
    assert deserialized_handler.delay == original_handler.delay
    assert deserialized_handler.utc == original_handler.utc
    assert deserialized_handler.atTime == original_handler.atTime
