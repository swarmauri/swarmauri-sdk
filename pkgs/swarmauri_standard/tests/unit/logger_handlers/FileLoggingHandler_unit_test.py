import pytest
import os
import logging
import tempfile
from unittest.mock import patch
from typing import Dict, Any

from swarmauri_standard.logger_handlers.FileLoggingHandler import FileLoggingHandler
from swarmauri_base.logger_formatters.FormatterBase import FormatterBase


@pytest.fixture
def temp_log_file():
    """
    Fixture providing a temporary log file path.

    Returns:
        str: Path to a temporary log file.
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".log") as temp_file:
        temp_path = temp_file.name

    yield temp_path

    # Clean up the file after the test
    if os.path.exists(temp_path):
        os.remove(temp_path)


@pytest.fixture
def simple_handler(temp_log_file):
    """
    Fixture providing a basic FileLoggingHandler instance.

    Args:
        temp_log_file: Temporary log file path from fixture.

    Returns:
        FileLoggingHandler: A configured handler instance.
    """
    return FileLoggingHandler(filepath=temp_log_file, level="INFO")


@pytest.fixture
def rotating_handler(temp_log_file):
    """
    Fixture providing a rotating FileLoggingHandler instance.

    Args:
        temp_log_file: Temporary log file path from fixture.

    Returns:
        FileLoggingHandler: A configured rotating handler instance.
    """
    return FileLoggingHandler(
        filepath=temp_log_file, level="DEBUG", max_bytes=1024, backup_count=3
    )


class MockFormatter(FormatterBase):
    """Mock formatter for testing."""

    type = "MockFormatter"

    def compile_formatter(self):
        """Return a mock formatter."""
        return logging.Formatter("[TEST] %(message)s")

    def get_config(self) -> Dict[str, Any]:
        """Get mock formatter config."""
        return {"type": self.type}


@pytest.mark.unit
def test_handler_initialization():
    """Test that the handler initializes with correct attributes."""
    handler = FileLoggingHandler(
        filepath="/tmp/test.log",
        mode="w",
        encoding="latin-1",
        delay=True,
        max_bytes=1024,
        backup_count=5,
        level="DEBUG",
    )

    assert handler.type == "FileLoggingHandler"
    assert handler.filepath == "/tmp/test.log"
    assert handler.mode == "w"
    assert handler.encoding == "latin-1"
    assert handler.delay is True
    assert handler.max_bytes == 1024
    assert handler.backup_count == 5
    assert handler.level == "DEBUG"


@pytest.mark.unit
def test_directory_creation():
    """Test that the handler creates the directory for the log file if it doesn't exist."""
    with tempfile.TemporaryDirectory() as temp_dir:
        log_dir = os.path.join(temp_dir, "logs")
        log_file = os.path.join(log_dir, "test.log")

        # Directory shouldn't exist yet
        assert not os.path.exists(log_dir)

        # Creating the handler should create the directory
        FileLoggingHandler(filepath=log_file)

        # Directory should now exist
        assert os.path.exists(log_dir)


@pytest.mark.unit
def test_compile_handler_standard(simple_handler):
    """Test compiling a standard file handler."""
    compiled = simple_handler.compile_handler()

    assert isinstance(compiled, logging.FileHandler)
    assert compiled.level == logging.INFO
    assert compiled.baseFilename == simple_handler.filepath


@pytest.mark.unit
def test_compile_handler_rotating(rotating_handler):
    """Test compiling a rotating file handler."""
    compiled = rotating_handler.compile_handler()

    assert isinstance(compiled, logging.handlers.RotatingFileHandler)
    assert compiled.level == logging.DEBUG
    assert compiled.baseFilename == rotating_handler.filepath
    assert compiled.maxBytes == 1024
    assert compiled.backupCount == 3


@pytest.mark.unit
def test_formatter_string():
    """Test handler with string formatter."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".log") as temp_file:
        handler = FileLoggingHandler(
            filepath=temp_file.name, formatter="%(levelname)s: %(message)s"
        )

        compiled = handler.compile_handler()
        assert isinstance(compiled.formatter, logging.Formatter)

        # Clean up
        os.remove(temp_file.name)


@pytest.mark.unit
def test_formatter_object():
    """Test handler with formatter object."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".log") as temp_file:
        mock_formatter = MockFormatter()

        handler = FileLoggingHandler(filepath=temp_file.name, formatter=mock_formatter)

        compiled = handler.compile_handler()
        assert isinstance(compiled.formatter, logging.Formatter)

        # Clean up
        os.remove(temp_file.name)


@pytest.mark.unit
def test_default_formatter():
    """Test that a default formatter is applied when none is provided."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".log") as temp_file:
        handler = FileLoggingHandler(filepath=temp_file.name)

        compiled = handler.compile_handler()
        assert compiled.formatter is not None

        # Clean up
        os.remove(temp_file.name)


@pytest.mark.unit
def test_actual_logging(simple_handler):
    """Test that the handler actually writes to the log file."""
    # Get the compiled handler
    handler = simple_handler.compile_handler()

    # Create a logger and add the handler
    logger = logging.getLogger("test_logger")
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    # Log a message
    test_message = "This is a test log message"
    logger.info(test_message)

    # Close the handler to ensure the message is written
    handler.close()

    # Read the log file and check the content
    with open(simple_handler.filepath, "r") as log_file:
        content = log_file.read()
        assert test_message in content


@pytest.mark.unit
def test_get_config_with_string_formatter():
    """Test get_config with string formatter."""
    handler = FileLoggingHandler(
        filepath="/tmp/test.log",
        formatter="%(levelname)s: %(message)s",
        level="WARNING",
    )

    config = handler.get_config()

    assert config["type"] == "FileLoggingHandler"
    assert config["filepath"] == "/tmp/test.log"
    assert config["formatter"] == "%(levelname)s: %(message)s"
    assert config["level"] == "WARNING"


@pytest.mark.unit
def test_get_config_with_object_formatter():
    """Test get_config with formatter object."""
    mock_formatter = MockFormatter()

    handler = FileLoggingHandler(filepath="/tmp/test.log", formatter=mock_formatter)

    config = handler.get_config()

    assert config["type"] == "FileLoggingHandler"
    assert config["filepath"] == "/tmp/test.log"
    assert config["formatter"]["type"] == "MockFormatter"


@pytest.mark.unit
def test_get_config_complete():
    """Test get_config returns all configuration parameters."""
    handler = FileLoggingHandler(
        filepath="/tmp/test.log",
        mode="w",
        encoding="latin-1",
        delay=True,
        max_bytes=1024,
        backup_count=5,
        level="DEBUG",
    )

    config = handler.get_config()

    assert config["type"] == "FileLoggingHandler"
    assert config["filepath"] == "/tmp/test.log"
    assert config["mode"] == "w"
    assert config["encoding"] == "latin-1"
    assert config["delay"] is True
    assert config["max_bytes"] == 1024
    assert config["backup_count"] == 5
    assert config["level"] == "DEBUG"


@pytest.mark.unit
@patch("os.makedirs")
def test_directory_creation_on_compile(mock_makedirs, temp_log_file):
    """Test directory creation when compiling the handler."""
    # Create a handler with a path in a non-existent directory
    test_dir = "/nonexistent/dir"
    test_path = f"{test_dir}/test.log"

    handler = FileLoggingHandler(filepath=test_path)

    # Reset the mock to clear the call from initialization
    mock_makedirs.reset_mock()

    # Compile the handler
    handler.compile_handler()

    # Check that makedirs was called with the directory path
    mock_makedirs.assert_called_once_with(test_dir, exist_ok=True)
