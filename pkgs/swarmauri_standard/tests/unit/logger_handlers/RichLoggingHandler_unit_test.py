import logging
from unittest.mock import MagicMock, mock_open, patch

import pytest
from rich.logging import RichHandler
from swarmauri_base.logger_formatters.FormatterBase import FormatterBase

from swarmauri_standard.logger_handlers.RichLoggingHandler import RichLoggingHandler


@pytest.fixture
def basic_handler():
    """
    Fixture providing a basic RichLoggingHandler instance.

    Returns
    -------
    RichLoggingHandler
        A basic RichLoggingHandler instance with default settings
    """
    return RichLoggingHandler()


@pytest.mark.unit
def test_rich_handler_initialization():
    """Test that the RichLoggingHandler initializes with default values."""
    handler = RichLoggingHandler()

    assert handler.type == "RichLoggingHandler"
    assert handler.level == logging.INFO
    assert handler.formatter is None
    assert handler.show_time is True
    assert handler.show_path is False
    assert handler.show_level is True
    assert handler.rich_tracebacks is True
    assert handler.console_kwargs == {}
    assert handler.enable_markup is True
    assert handler.log_file_path is None


@pytest.mark.unit
@pytest.mark.parametrize(
    "level",
    [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL],
)
def test_handler_with_different_levels(level):
    """Test that the handler can be configured with different logging levels."""
    handler = RichLoggingHandler(level=level)
    assert handler.level == level

    # Compile and check the created handler
    rich_handler = handler.compile_handler()
    assert isinstance(rich_handler, RichHandler)
    assert rich_handler.level == level


@pytest.mark.unit
def test_handler_with_string_formatter():
    """Test that the handler accepts and applies a string formatter."""
    format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    handler = RichLoggingHandler(formatter=format_string)

    # Compile and check the formatter
    rich_handler = handler.compile_handler()
    assert isinstance(rich_handler.formatter, logging.Formatter)
    assert rich_handler.formatter._fmt == format_string


@pytest.mark.unit
def test_handler_with_formatter_object():
    """Test that the handler accepts and applies a FormatterBase object."""
    # Create a mock formatter with proper attributes for Pydantic validation
    mock_formatter = MagicMock(spec=FormatterBase)
    mock_formatter.type = "FormatterBase"
    mock_formatter.model_dump = MagicMock(return_value={"type": "FormatterBase"})
    mock_formatter.compile_formatter.return_value = logging.Formatter(
        "%(levelname)s: %(message)s"
    )

    handler = RichLoggingHandler(formatter=mock_formatter)

    # Compile and check the formatter
    rich_handler = handler.compile_handler()
    assert mock_formatter.compile_formatter.called
    assert isinstance(rich_handler.formatter, logging.Formatter)


@pytest.mark.unit
@pytest.mark.parametrize(
    "show_time,show_path,show_level",
    [
        (True, True, True),
        (False, False, False),
        (True, False, True),
        (False, True, False),
    ],
)
def test_handler_display_options(show_time, show_path, show_level):
    """Test that display options are correctly passed to the RichHandler."""
    handler = RichLoggingHandler(
        show_time=show_time, show_path=show_path, show_level=show_level
    )

    with patch(
        "swarmauri_standard.logger_handlers.RichLoggingHandler.RichHandler"
    ) as mock_rich_handler:
        handler.compile_handler()
        mock_rich_handler.assert_called_once()
        # Check that the options were passed correctly
        call_kwargs = mock_rich_handler.call_args[1]
        assert call_kwargs["show_time"] == show_time
        assert call_kwargs["show_path"] == show_path
        assert call_kwargs["show_level"] == show_level


@pytest.mark.unit
def test_handler_with_console_kwargs():
    """Test that console_kwargs are correctly passed to the Console."""
    console_kwargs = {"width": 100, "color_system": "auto", "highlight": False}
    handler = RichLoggingHandler(console_kwargs=console_kwargs)

    with patch(
        "swarmauri_standard.logger_handlers.RichLoggingHandler.Console"
    ) as mock_console:
        handler.compile_handler()
        mock_console.assert_called_once_with(**console_kwargs)


@pytest.mark.unit
def test_handler_with_log_file():
    """Test that log_file_path creates a file for logging."""
    log_path = "test_logs/test.log"
    handler = RichLoggingHandler(log_file_path=log_path)

    # Mock the file operations
    with (
        patch("os.path.exists", return_value=False) as mock_exists,
        patch("os.makedirs") as mock_makedirs,
        patch("builtins.open", mock_open()) as mock_file,
        patch(
            "swarmauri_standard.logger_handlers.RichLoggingHandler.Console"
        ) as mock_console,
    ):
        handler.compile_handler()

        # Check directory creation
        mock_exists.assert_called_once_with("test_logs")
        mock_makedirs.assert_called_once_with("test_logs")

        # Check file opening
        mock_file.assert_called_once_with(log_path, "a", encoding="utf-8")

        # Check console creation with file
        mock_console.assert_called_once()
        assert "file" in mock_console.call_args[1]


@pytest.mark.unit
def test_handler_with_existing_log_directory():
    """Test that existing log directories are not recreated."""
    log_path = "existing_logs/test.log"
    handler = RichLoggingHandler(log_file_path=log_path)

    # Mock the file operations
    with (
        patch("os.path.exists", return_value=True) as mock_exists,
        patch("os.makedirs") as mock_makedirs,
        patch("builtins.open", mock_open()) as mock_file,
    ):
        handler.compile_handler()

        # Check directory existence check
        mock_exists.assert_called_once_with("existing_logs")
        # Ensure makedirs was not called since directory exists
        mock_makedirs.assert_not_called()

        # Check file opening
        mock_file.assert_called_once_with(log_path, "a", encoding="utf-8")


@pytest.mark.unit
def test_handler_with_enable_markup():
    """Test that enable_markup flag is correctly passed to RichHandler."""
    # Test with markup enabled
    handler_markup_enabled = RichLoggingHandler(enable_markup=True)
    with patch(
        "swarmauri_standard.logger_handlers.RichLoggingHandler.RichHandler"
    ) as mock_rich_handler:
        handler_markup_enabled.compile_handler()
        call_kwargs = mock_rich_handler.call_args[1]
        assert call_kwargs["markup"] is True  # Only check for markup

    # Test with markup disabled
    handler_markup_disabled = RichLoggingHandler(enable_markup=False)
    with patch(
        "swarmauri_standard.logger_handlers.RichLoggingHandler.RichHandler"
    ) as mock_rich_handler:
        handler_markup_disabled.compile_handler()
        call_kwargs = mock_rich_handler.call_args[1]
        assert call_kwargs["markup"] is False  # Only check for markup


@pytest.mark.unit
def test_rich_tracebacks_option():
    """Test that rich_tracebacks option is correctly passed to RichHandler."""
    # Test with rich tracebacks enabled
    handler_tracebacks_enabled = RichLoggingHandler(rich_tracebacks=True)
    with patch(
        "swarmauri_standard.logger_handlers.RichLoggingHandler.RichHandler"
    ) as mock_rich_handler:
        handler_tracebacks_enabled.compile_handler()
        call_kwargs = mock_rich_handler.call_args[1]
        assert call_kwargs["rich_tracebacks"] is True

    # Test with rich tracebacks disabled
    handler_tracebacks_disabled = RichLoggingHandler(rich_tracebacks=False)
    with patch(
        "swarmauri_standard.logger_handlers.RichLoggingHandler.RichHandler"
    ) as mock_rich_handler:
        handler_tracebacks_disabled.compile_handler()
        call_kwargs = mock_rich_handler.call_args[1]
        assert call_kwargs["rich_tracebacks"] is False


@pytest.mark.unit
def test_integration_with_logging_system(basic_handler):
    """Test integration with Python's logging system."""
    # Create a logger
    logger = logging.getLogger("test_rich_handler")
    logger.setLevel(logging.DEBUG)

    # Clear any existing handlers
    logger.handlers = []

    # Add our handler
    rich_handler = basic_handler.compile_handler()
    logger.addHandler(rich_handler)

    # Test that logging works without errors
    with patch.object(rich_handler, "emit") as mock_emit:
        logger.info("Test log message")
        assert mock_emit.called


@pytest.mark.unit
def test_log_file_creation_with_no_directory():
    """Test logging to a file with no parent directory."""
    log_path = "test.log"  # No directory part
    handler = RichLoggingHandler(log_file_path=log_path)

    with (
        patch("builtins.open", mock_open()) as mock_file,
    ):
        handler.compile_handler()

        # Check file opening without directory creation attempts
        mock_file.assert_called_once_with(log_path, "a", encoding="utf-8")
