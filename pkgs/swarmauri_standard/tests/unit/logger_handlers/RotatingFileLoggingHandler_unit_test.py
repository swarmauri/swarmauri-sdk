import logging
import os
import shutil
import tempfile
from unittest.mock import MagicMock, patch

import pytest
from swarmauri_base.logger_formatters.FormatterBase import FormatterBase

from swarmauri_standard.logger_handlers.RotatingFileLoggingHandler import (
    RotatingFileLoggingHandler,
)


@pytest.fixture
def temp_log_file():
    """
    Creates a temporary log file for testing.

    Returns
    -------
    str
        Path to the temporary log file.
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".log") as temp_file:
        temp_path = temp_file.name
    yield temp_path

    # Clean up after the test
    if os.path.exists(temp_path):
        os.remove(temp_path)


@pytest.mark.unit
def test_default_attributes():
    """
    Tests that the default attributes of RotatingFileLoggingHandler are set correctly.
    """
    handler = RotatingFileLoggingHandler()

    assert handler.type == "RotatingFileLoggingHandler"
    assert handler.level == logging.INFO
    assert handler.formatter is None
    assert handler.filename == "app.log"
    assert handler.maxBytes == 10485760  # 10 MB
    assert handler.backupCount == 5
    assert handler.encoding is None
    assert handler.delay is False


@pytest.mark.unit
def test_custom_attributes():
    """
    Tests that custom attributes are correctly set during initialization.
    """
    handler = RotatingFileLoggingHandler(
        level=logging.DEBUG,
        formatter="%(message)s",
        filename="custom.log",
        maxBytes=1024,
        backupCount=3,
        encoding="utf-8",
        delay=True,
    )

    assert handler.level == logging.DEBUG
    assert handler.formatter == "%(message)s"
    assert handler.filename == "custom.log"
    assert handler.maxBytes == 1024
    assert handler.backupCount == 3
    assert handler.encoding == "utf-8"
    assert handler.delay is True


@pytest.mark.unit
def test_compile_handler_creates_directory(temp_log_file):
    log_dir = os.path.join(os.path.dirname(temp_log_file), "new_dir")
    log_file = os.path.join(log_dir, "test.log")

    # Ensure directory doesn't exist before test
    if os.path.exists(log_dir):
        shutil.rmtree(log_dir)

    handler = RotatingFileLoggingHandler(filename=log_file)

    # Directory should not exist yet
    assert not os.path.exists(log_dir)

    # Compile the handler
    handler.compile_handler()

    # Directory should now exist
    assert os.path.exists(log_dir)

    # Clean up
    shutil.rmtree(log_dir)  # Use rmtree instead of rmdir in case files were created


@pytest.mark.unit
def test_compile_handler_returns_rotating_file_handler(temp_log_file):
    """
    Tests that compile_handler returns a RotatingFileHandler instance.
    """
    handler = RotatingFileLoggingHandler(filename=temp_log_file)
    compiled_handler = handler.compile_handler()

    assert isinstance(compiled_handler, logging.handlers.RotatingFileHandler)
    assert compiled_handler.level == logging.INFO
    assert compiled_handler.baseFilename == temp_log_file
    assert compiled_handler.maxBytes == 10485760
    assert compiled_handler.backupCount == 5


@pytest.mark.unit
def test_compile_handler_with_string_formatter(temp_log_file):
    """
    Tests that compile_handler correctly applies a string formatter.
    """
    format_string = "%(levelname)s: %(message)s"
    handler = RotatingFileLoggingHandler(
        filename=temp_log_file, formatter=format_string
    )

    compiled_handler = handler.compile_handler()

    assert isinstance(compiled_handler.formatter, logging.Formatter)
    assert compiled_handler.formatter._fmt == format_string


@pytest.mark.unit
def test_compile_handler_with_formatter_object():
    """
    Tests that compile_handler correctly applies a FormatterBase object.
    """
    # Create a mock formatter
    mock_formatter = MagicMock(spec=FormatterBase)
    mock_formatter.type = "FormatterBase"  # Must be exactly "FormatterBase"
    mock_formatter.model_dump = MagicMock(return_value={"type": "FormatterBase"})
    mock_formatter.compile_formatter.return_value = logging.Formatter(
        "%(levelname)s: %(message)s"
    )

    handler = RotatingFileLoggingHandler(formatter=mock_formatter)
    compiled_handler = handler.compile_handler()

    # Verify the formatter was called and set correctly
    mock_formatter.compile_formatter.assert_called_once()
    assert compiled_handler.formatter == mock_formatter.compile_formatter.return_value


@pytest.mark.unit
def test_compile_handler_uses_default_formatter_when_none_specified(temp_log_file):
    """
    Tests that compile_handler sets a default formatter when none is specified.
    """
    handler = RotatingFileLoggingHandler(filename=temp_log_file, formatter=None)
    compiled_handler = handler.compile_handler()

    assert isinstance(compiled_handler.formatter, logging.Formatter)
    assert (
        compiled_handler.formatter._fmt
        == "[%(asctime)s][%(name)s][%(levelname)s] %(message)s"
    )
    assert compiled_handler.formatter.datefmt == "%Y-%m-%d %H:%M:%S"


@pytest.mark.unit
def test_serialization():
    """
    Tests that the handler can be serialized and deserialized correctly.
    """
    original_handler = RotatingFileLoggingHandler(
        level=logging.DEBUG, filename="test.log", maxBytes=2048, backupCount=2
    )

    # Serialize to JSON
    json_data = original_handler.model_dump_json()

    # Deserialize from JSON
    deserialized_handler = RotatingFileLoggingHandler.model_validate_json(json_data)

    # Check that the deserialized handler has the same attributes
    assert deserialized_handler.level == original_handler.level
    assert deserialized_handler.filename == original_handler.filename
    assert deserialized_handler.maxBytes == original_handler.maxBytes
    assert deserialized_handler.backupCount == original_handler.backupCount


@pytest.mark.unit
@patch(
    "swarmauri_standard.logger_handlers.RotatingFileLoggingHandler.RotatingFileHandler"
)
def test_handler_initialization_parameters(mock_rotating_handler, temp_log_file):
    """
    Tests that the correct parameters are passed to RotatingFileHandler.
    """
    # Create a handler with custom parameters
    handler = RotatingFileLoggingHandler(
        filename=temp_log_file,
        maxBytes=1024,
        backupCount=3,
        encoding="utf-8",
        delay=True,
    )

    # Compile the handler
    handler.compile_handler()

    # Verify RotatingFileHandler was called with correct parameters
    mock_rotating_handler.assert_called_once_with(
        filename=temp_log_file,
        maxBytes=1024,
        backupCount=3,
        encoding="utf-8",
        delay=True,
    )
