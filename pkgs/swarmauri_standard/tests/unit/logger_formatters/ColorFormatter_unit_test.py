import io
import logging

import pytest

from swarmauri_standard.logger_formatters.ColorFormatter import ColorFormatter


@pytest.fixture
def color_formatter():
    """
    Fixture that returns a default ColorFormatter instance.

    Returns:
        ColorFormatter: A new instance with default settings
    """
    return ColorFormatter()


@pytest.mark.unit
def test_default_initialization():
    """
    Test that ColorFormatter initializes with expected default values.
    """
    formatter = ColorFormatter()
    assert formatter.format == "[%(name)s] [%(levelname)s] %(message)s"
    assert formatter.date_format == "%Y-%m-%d %H:%M:%S"
    assert formatter.use_colors is True
    assert formatter.include_timestamp is False
    assert formatter.include_process is False
    assert formatter.include_thread is False


@pytest.mark.unit
def test_custom_initialization():
    """
    Test that ColorFormatter initializes correctly with custom values.
    """
    formatter = ColorFormatter(
        include_timestamp=True,
        include_process=True,
        include_thread=True,
        use_colors=False,
    )

    assert formatter.include_timestamp is True
    assert formatter.include_process is True
    assert formatter.include_thread is True
    assert formatter.use_colors is False


@pytest.mark.unit
def test_model_post_init():
    """
    Test that model_post_init correctly updates the format string based on configuration.
    """
    # Test with all options enabled
    formatter = ColorFormatter(
        include_timestamp=True, include_process=True, include_thread=True
    )
    formatter.model_post_init()

    assert "%(asctime)s" in formatter.format
    assert "[%(name)s]" in formatter.format
    assert "[%(levelname)s]" in formatter.format
    assert "Process:%(process)d" in formatter.format
    assert "Thread:%(thread)d" in formatter.format
    assert "%(message)s" in formatter.format


@pytest.mark.unit
def test_disable_enable_colors(color_formatter):
    """
    Test that color enabling/disabling methods work correctly.

    Args:
        color_formatter: Fixture providing a ColorFormatter instance
    """
    assert color_formatter.is_using_colors() is True

    color_formatter.disable_colors()
    assert color_formatter.is_using_colors() is False

    color_formatter.enable_colors()
    assert color_formatter.is_using_colors() is True


@pytest.mark.unit
def test_compile_formatter_without_colors():
    """
    Test that compile_formatter returns a standard formatter when colors are disabled.
    """
    formatter = ColorFormatter(use_colors=False)
    log_formatter = formatter.compile_formatter()

    # Should be a standard logging.Formatter when colors are disabled
    assert isinstance(log_formatter, logging.Formatter)
    assert not hasattr(log_formatter, "colors")


@pytest.mark.unit
def test_compile_formatter_with_colors():
    """
    Test that compile_formatter returns a custom formatter when colors are enabled.
    """
    formatter = ColorFormatter(use_colors=True)
    log_formatter = formatter.compile_formatter()

    # Should be a custom ColoredFormatter when colors are enabled
    assert isinstance(log_formatter, logging.Formatter)
    assert hasattr(log_formatter, "colors")
    assert hasattr(log_formatter, "reset")


@pytest.mark.unit
@pytest.mark.parametrize(
    "level,color_code",
    [
        (logging.DEBUG, "\033[36m"),  # Cyan
        (logging.INFO, "\033[32m"),  # Green
        (logging.WARNING, "\033[33m"),  # Yellow
        (logging.ERROR, "\033[31m"),  # Red
        (logging.CRITICAL, "\033[41m"),  # Red background
    ],
)
def test_color_codes_by_level(level, color_code):
    """
    Test that the correct color codes are applied for each log level.

    Args:
        level: The logging level to test
        color_code: The expected ANSI color code for the level
    """
    formatter = ColorFormatter()
    log_formatter = formatter.compile_formatter()

    # Create a log record with the specified level
    record = logging.LogRecord(
        name="test_logger",
        level=level,
        pathname="",
        lineno=0,
        msg="Test message",
        args=(),
        exc_info=None,
    )

    # Format the record
    formatted = log_formatter.format(record)

    # The color code should be in the formatted string
    assert color_code in formatted
    assert "\033[0m" in formatted  # Reset code should also be present


@pytest.mark.unit
def test_actual_logging_output():
    """
    Test the actual output produced when using the formatter with a logger.
    """
    # Create a logger with a stream handler
    logger = logging.getLogger("test_color_formatter")
    logger.setLevel(logging.DEBUG)

    # Use a StringIO to capture the output
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)

    # Apply our formatter to the handler
    formatter = ColorFormatter()
    handler.setFormatter(formatter.compile_formatter())

    # Add the handler to the logger
    logger.addHandler(handler)

    # Log messages at different levels
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")

    # Get the output
    output = stream.getvalue()

    # Check that the output contains color codes
    assert "\033[36m" in output  # Cyan for DEBUG
    assert "\033[32m" in output  # Green for INFO
    assert "\033[33m" in output  # Yellow for WARNING
    assert "\033[31m" in output  # Red for ERROR
    assert "\033[41m" in output  # Red background for CRITICAL
    assert "\033[0m" in output  # Reset code

    # Clean up
    logger.removeHandler(handler)


@pytest.mark.unit
def test_formatter_without_colors_actual_output():
    """
    Test the actual output produced when colors are disabled.
    """
    # Create a logger with a stream handler
    logger = logging.getLogger("test_no_color_formatter")
    logger.setLevel(logging.DEBUG)

    # Use a StringIO to capture the output
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)

    # Apply our formatter to the handler with colors disabled
    formatter = ColorFormatter(use_colors=False)
    handler.setFormatter(formatter.compile_formatter())

    # Add the handler to the logger
    logger.addHandler(handler)

    # Log a message
    logger.info("This is a test message")

    # Get the output
    output = stream.getvalue()

    # Check that the output doesn't contain color codes
    assert "\033[" not in output

    # Clean up
    logger.removeHandler(handler)
