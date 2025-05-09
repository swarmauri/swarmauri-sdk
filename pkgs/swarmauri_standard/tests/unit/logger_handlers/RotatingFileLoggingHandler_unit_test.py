import os
import logging
import tempfile
import pytest
from unittest.mock import patch, MagicMock
from logging.handlers import RotatingFileHandler

from swarmauri_standard.logger_handlers.RotatingFileLoggingHandler import (
    RotatingFileLoggingHandler,
)
from swarmauri_base.logger_formatters.FormatterBase import FormatterBase


@pytest.fixture
def temp_log_file():
    """
    Fixture that creates a temporary log file for testing.

    Returns
    -------
    str
        Path to the temporary log file.
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".log") as tmp:
        tmp_path = tmp.name

    yield tmp_path

    # Clean up after the test
    if os.path.exists(tmp_path):
        os.unlink(tmp_path)


@pytest.fixture
def rotating_handler(temp_log_file):
    """
    Fixture that creates a RotatingFileLoggingHandler instance for testing.

    Parameters
    ----------
    temp_log_file : str
        Path to the temporary log file.

    Returns
    -------
    RotatingFileLoggingHandler
        An instance of RotatingFileLoggingHandler.
    """
    return RotatingFileLoggingHandler(
        filename=temp_log_file, maxBytes=1000, backupCount=3, level=logging.INFO
    )


@pytest.mark.unit
def test_type():
    """Test that the handler type is correctly set."""
    assert RotatingFileLoggingHandler.type == "RotatingFileLoggingHandler"


@pytest.mark.unit
def test_default_values():
    """Test the default values for the handler attributes."""
    handler = RotatingFileLoggingHandler(filename="/tmp/test.log")
    assert handler.maxBytes == 1048576  # 1MB
    assert handler.backupCount == 5
    assert handler.encoding is None
    assert handler.delay is False


@pytest.mark.unit
def test_initialization(temp_log_file):
    """Test initialization with custom parameters."""
    handler = RotatingFileLoggingHandler(
        filename=temp_log_file,
        maxBytes=2000000,
        backupCount=10,
        encoding="utf-8",
        delay=True,
        level=logging.DEBUG,
    )

    assert handler.filename == temp_log_file
    assert handler.maxBytes == 2000000
    assert handler.backupCount == 10
    assert handler.encoding == "utf-8"
    assert handler.delay is True
    assert handler.level == logging.DEBUG


@pytest.mark.unit
def test_directory_creation():
    """Test that the handler creates the directory for the log file if it doesn't exist."""
    with tempfile.TemporaryDirectory() as temp_dir:
        non_existent_dir = os.path.join(temp_dir, "logs", "app")
        log_file = os.path.join(non_existent_dir, "test.log")

        # Verify directory doesn't exist yet
        assert not os.path.exists(non_existent_dir)

        # Initialize handler, which should create the directory
        RotatingFileLoggingHandler(filename=log_file)

        # Verify directory was created
        assert os.path.exists(non_existent_dir)


@pytest.mark.unit
def test_compile_handler_basic(rotating_handler):
    """Test that compile_handler returns a properly configured RotatingFileHandler."""
    handler = rotating_handler.compile_handler()

    assert isinstance(handler, RotatingFileHandler)
    assert handler.baseFilename == rotating_handler.filename
    assert handler.maxBytes == rotating_handler.maxBytes
    assert handler.backupCount == rotating_handler.backupCount
    assert handler.level == rotating_handler.level


@pytest.mark.unit
def test_compile_handler_with_string_formatter():
    """Test compile_handler with a string formatter."""
    formatter_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    with tempfile.NamedTemporaryFile(delete=False, suffix=".log") as tmp:
        handler = RotatingFileLoggingHandler(
            filename=tmp.name, formatter=formatter_string
        )

        compiled_handler = handler.compile_handler()

        # Check that the formatter was set correctly
        assert compiled_handler.formatter._fmt == formatter_string

        # Clean up
        os.unlink(tmp.name)


@pytest.mark.unit
def test_compile_handler_with_formatter_object():
    """Test compile_handler with a FormatterBase object."""
    mock_formatter = MagicMock(spec=FormatterBase)
    mock_formatter.compile_formatter.return_value = logging.Formatter(
        "%(levelname)s: %(message)s"
    )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".log") as tmp:
        handler = RotatingFileLoggingHandler(
            filename=tmp.name, formatter=mock_formatter
        )

        handler.compile_handler()

        # Verify that compile_formatter was called
        mock_formatter.compile_formatter.assert_called_once()

        # Clean up
        os.unlink(tmp.name)


@pytest.mark.unit
def test_compile_handler_default_formatter(rotating_handler):
    """Test that a default formatter is used when none is specified."""
    compiled_handler = rotating_handler.compile_handler()

    # Check that a formatter was set
    assert compiled_handler.formatter is not None

    # Check that the format string includes typical default components
    fmt_str = compiled_handler.formatter._fmt
    assert "[%(asctime)s]" in fmt_str
    assert "[%(name)s]" in fmt_str
    assert "[%(levelname)s]" in fmt_str
    assert "%(message)s" in fmt_str


@pytest.mark.unit
def test_to_dict(rotating_handler):
    """Test that to_dict returns the correct dictionary representation."""
    result = rotating_handler.to_dict()

    assert result["type"] == "RotatingFileLoggingHandler"
    assert result["filename"] == rotating_handler.filename
    assert result["maxBytes"] == rotating_handler.maxBytes
    assert result["backupCount"] == rotating_handler.backupCount
    assert result["level"] == rotating_handler.level
    assert "encoding" not in result  # Should not include None values
    assert "delay" not in result  # Default False should not be included


@pytest.mark.unit
def test_to_dict_with_all_attributes():
    """Test to_dict with all attributes specified."""
    handler = RotatingFileLoggingHandler(
        filename="/tmp/test.log",
        maxBytes=5000000,
        backupCount=7,
        encoding="utf-8",
        delay=True,
        level=logging.WARNING,
    )

    result = handler.to_dict()

    assert result["filename"] == "/tmp/test.log"
    assert result["maxBytes"] == 5000000
    assert result["backupCount"] == 7
    assert result["encoding"] == "utf-8"
    assert result["delay"] is True
    assert result["level"] == logging.WARNING


@pytest.mark.unit
@patch("logging.handlers.RotatingFileHandler")
def test_handler_rotation(mock_rotating_handler, temp_log_file):
    """Test that the handler correctly configures rotation parameters."""
    # Set up the mock
    mock_instance = MagicMock()
    mock_rotating_handler.return_value = mock_instance

    # Create and compile the handler
    handler = RotatingFileLoggingHandler(
        filename=temp_log_file, maxBytes=2048, backupCount=4, level=logging.INFO
    )

    handler.compile_handler()

    # Verify the handler was created with correct parameters
    mock_rotating_handler.assert_called_once_with(
        filename=temp_log_file, maxBytes=2048, backupCount=4, encoding=None, delay=False
    )


@pytest.mark.unit
def test_functional_logging(temp_log_file):
    """Test that the handler can actually write log messages to a file."""
    # Create the handler
    handler = RotatingFileLoggingHandler(filename=temp_log_file, level=logging.INFO)

    # Set up a logger that uses this handler
    logger = logging.getLogger("test_rotating_file_handler")
    logger.setLevel(logging.INFO)
    logger.addHandler(handler.compile_handler())

    # Write a log message
    test_message = "This is a test log message"
    logger.info(test_message)

    # Verify the message was written to the file
    with open(temp_log_file, "r") as f:
        log_content = f.read()
        assert test_message in log_content
