import logging
import os
import shutil
import tempfile
from logging.handlers import RotatingFileHandler
from unittest.mock import MagicMock, patch

import pytest
from swarmauri_base.logger_formatters.FormatterBase import FormatterBase

from swarmauri_standard.logger_handlers.FileLoggingHandler import FileLoggingHandler


@pytest.fixture
def temp_log_file():
    """
    Creates a temporary file for testing logging.

    Returns:
        str: Path to the temporary log file.
    """
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_path = temp_file.name

    yield temp_path

    # Clean up the file after the test
    if os.path.exists(temp_path):
        os.remove(temp_path)


@pytest.mark.unit
def test_file_logging_handler_default_values():
    """Tests that FileLoggingHandler initializes with correct default values."""
    handler = FileLoggingHandler()

    assert handler.type == "FileLoggingHandler"
    assert handler.level == logging.INFO
    assert handler.formatter is None
    assert handler.file_path == "logs/app.log"
    assert handler.file_mode == "a"
    assert handler.encoding == "utf-8"
    assert handler.max_bytes == 0
    assert handler.backup_count == 0


@pytest.mark.unit
def test_compile_handler_creates_directory(temp_log_file):
    """Tests that compile_handler creates the log directory if it doesn't exist."""
    # Create a path in a non-existent directory
    log_dir = os.path.join(os.path.dirname(temp_log_file), "test_logs")
    log_path = os.path.join(log_dir, "test.log")

    # Make sure directory doesn't exist before test
    if os.path.exists(log_dir):
        shutil.rmtree(log_dir)  # Remove directory and all contents

    handler = FileLoggingHandler(file_path=log_path)

    # Directory should not exist yet
    assert not os.path.exists(log_dir)

    # Compile handler should create the directory
    compiled_handler = handler.compile_handler()

    # Directory should now exist
    assert os.path.exists(log_dir)

    # Clean up
    compiled_handler.close()
    # And use rmtree again for cleanup to handle any files created by the handler
    shutil.rmtree(log_dir)


@pytest.mark.unit
def test_compile_handler_creates_file_handler():
    """Tests that compile_handler creates a FileHandler when max_bytes is 0."""
    handler = FileLoggingHandler(max_bytes=0)

    with patch("logging.FileHandler") as mock_file_handler:
        mock_instance = MagicMock()
        mock_file_handler.return_value = mock_instance

        compiled_handler = handler.compile_handler()

        mock_file_handler.assert_called_once_with(
            filename="logs/app.log", mode="a", encoding="utf-8"
        )

        assert compiled_handler == mock_instance


@pytest.mark.unit
def test_compile_handler_creates_rotating_file_handler():
    """Tests that compile_handler creates a RotatingFileHandler when max_bytes > 0."""
    handler = FileLoggingHandler(max_bytes=1024, backup_count=3)

    # Fix the patch to match how RotatingFileHandler is imported in the implementation
    with patch(
        "swarmauri_standard.logger_handlers.FileLoggingHandler.RotatingFileHandler"
    ) as mock_rotating_handler:
        mock_instance = MagicMock()
        mock_rotating_handler.return_value = mock_instance

        compiled_handler = handler.compile_handler()

        mock_rotating_handler.assert_called_once_with(
            filename="logs/app.log",
            mode="a",
            maxBytes=1024,
            backupCount=3,
            encoding="utf-8",
        )

        assert compiled_handler == mock_instance


@pytest.mark.unit
def test_handler_sets_level():
    """Tests that the handler sets the correct logging level."""
    handler = FileLoggingHandler(level=logging.DEBUG)

    with patch("logging.FileHandler") as mock_file_handler:
        mock_instance = MagicMock()
        mock_file_handler.return_value = mock_instance

        handler.compile_handler()

        mock_instance.setLevel.assert_called_once_with(logging.DEBUG)


@pytest.mark.unit
def test_handler_with_string_formatter():
    """Tests that the handler correctly applies a string formatter."""
    format_string = "%(levelname)s: %(message)s"
    handler = FileLoggingHandler(formatter=format_string)

    with patch("logging.FileHandler") as mock_file_handler:
        mock_instance = MagicMock()
        mock_file_handler.return_value = mock_instance

        with patch("logging.Formatter") as mock_formatter:
            formatter_instance = MagicMock()
            mock_formatter.return_value = formatter_instance

            handler.compile_handler()

            mock_formatter.assert_called_with(format_string)
            mock_instance.setFormatter.assert_called_with(formatter_instance)


@pytest.mark.unit
def test_handler_with_formatter_object():
    """Tests that the handler correctly applies a FormatterBase object."""
    mock_formatter = MagicMock(spec=FormatterBase)
    mock_formatter.type = "FormatterBase"  # Add type for Pydantic validation
    mock_formatter.model_dump = MagicMock(return_value={"type": "FormatterBase"})
    compiled_formatter = MagicMock()
    mock_formatter.compile_formatter.return_value = compiled_formatter

    handler = FileLoggingHandler(formatter=mock_formatter)

    with patch("logging.FileHandler") as mock_file_handler:
        mock_instance = MagicMock()
        mock_file_handler.return_value = mock_instance

        handler.compile_handler()

        mock_formatter.compile_formatter.assert_called_once()
        mock_instance.setFormatter.assert_called_with(compiled_formatter)


@pytest.mark.unit
def test_handler_with_default_formatter():
    """Tests that the handler applies a default formatter when none is specified."""
    handler = FileLoggingHandler(formatter=None)

    with patch("logging.FileHandler") as mock_file_handler:
        mock_instance = MagicMock()
        mock_file_handler.return_value = mock_instance

        with patch("logging.Formatter") as mock_formatter:
            formatter_instance = MagicMock()
            mock_formatter.return_value = formatter_instance

            handler.compile_handler()

            mock_formatter.assert_called_with(
                "[%(asctime)s][%(name)s][%(levelname)s] %(message)s",
                "%Y-%m-%d %H:%M:%S",
            )
            mock_instance.setFormatter.assert_called_with(formatter_instance)


@pytest.mark.unit
def test_functional_file_handler(temp_log_file):
    """Functional test that verifies the handler actually writes to a file."""
    # Create handler with the temp file
    handler = FileLoggingHandler(file_path=temp_log_file, level=logging.DEBUG)

    # Compile the handler
    compiled_handler = handler.compile_handler()

    # Create a logger and add the handler
    logger = logging.getLogger("test_logger")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(compiled_handler)

    # Log a test message
    test_message = "This is a test log message"
    logger.debug(test_message)

    # Close the handler to ensure the message is written
    compiled_handler.close()

    # Verify the message was written to the file
    with open(temp_log_file, "r") as f:
        log_content = f.read()

    assert test_message in log_content


@pytest.mark.unit
def test_functional_rotating_file_handler(temp_log_file):
    """Functional test that verifies the rotating handler works correctly."""
    # Create a rotating handler with small max_bytes to trigger rotation
    handler = FileLoggingHandler(
        file_path=temp_log_file,
        level=logging.DEBUG,
        max_bytes=50,
        backup_count=2,
    )

    # Compile the handler
    compiled_handler = handler.compile_handler()

    # Verify it's a RotatingFileHandler
    assert isinstance(compiled_handler, RotatingFileHandler)

    # Create a logger and add the handler
    logger = logging.getLogger("test_rotating_logger")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(compiled_handler)

    # Log multiple messages to trigger rotation
    for i in range(10):
        logger.debug(f"Test log message {i} that should cause rotation")

    # Close the handler to ensure all messages are written
    compiled_handler.close()

    # Verify the log file exists
    assert os.path.exists(temp_log_file)

    # Check if backup files were created (at least one)
    backup_file = f"{temp_log_file}.1"
    assert os.path.exists(backup_file)

    # Clean up backup file
    if os.path.exists(backup_file):
        os.remove(backup_file)
