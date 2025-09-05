import io
import logging

import pytest

from swarmauri_standard.logger_formatters.BorderFormatter import BorderFormatter


@pytest.fixture
def border_formatter() -> BorderFormatter:
    """
    Create a basic BorderFormatter instance for testing.

    Returns:
        BorderFormatter: A default instance of BorderFormatter
    """
    return BorderFormatter()


@pytest.fixture
def log_record() -> logging.LogRecord:
    """
    Create a sample log record for testing.

    Returns:
        logging.LogRecord: A sample log record
    """
    return logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test_path",
        lineno=42,
        msg="Test message",
        args=(),
        exc_info=None,
    )


@pytest.mark.unit
def test_border_formatter_initialization() -> None:
    """Test that BorderFormatter initializes with default values."""
    formatter = BorderFormatter()

    assert formatter.border_char == "-"
    assert formatter.border_width == 80
    assert formatter.padding == 1


@pytest.mark.unit
def test_border_formatter_custom_initialization() -> None:
    """Test that BorderFormatter initializes with custom values."""
    formatter = BorderFormatter(border_char="*", border_width=60, padding=2)

    assert formatter.border_char == "*"
    assert formatter.border_width == 60
    assert formatter.padding == 2


@pytest.mark.unit
def test_set_border_style() -> None:
    """Test that set_border_style updates the border configuration."""
    formatter = BorderFormatter()

    formatter.set_border_style(char="#", width=40, padding=0)

    assert formatter.border_char == "#"
    assert formatter.border_width == 40
    assert formatter.padding == 0


@pytest.mark.unit
def test_apply_border() -> None:
    """Test that _apply_border correctly surrounds a message with borders."""
    formatter = BorderFormatter(border_char="-", border_width=10, padding=1)

    message = "Hello"
    bordered_message = formatter._apply_border(message)

    expected_lines = [
        "----------",  # Top border
        "",  # Padding
        "Hello",  # Message
        "",  # Padding
        "----------",  # Bottom border
    ]
    expected = "\n".join(expected_lines)

    assert bordered_message == expected


@pytest.mark.unit
def test_apply_border_no_padding() -> None:
    """Test that _apply_border works correctly with no padding."""
    formatter = BorderFormatter(border_char="=", border_width=10, padding=0)

    message = "Test"
    bordered_message = formatter._apply_border(message)

    expected_lines = [
        "==========",  # Top border
        "Test",  # Message
        "==========",  # Bottom border
    ]
    expected = "\n".join(expected_lines)

    assert bordered_message == expected


@pytest.mark.unit
def test_apply_border_multiline_message() -> None:
    """Test that _apply_border correctly handles multiline messages."""
    formatter = BorderFormatter(border_char="*", border_width=10, padding=1)

    message = "Line 1\nLine 2"
    bordered_message = formatter._apply_border(message)

    expected_lines = [
        "**********",  # Top border
        "",  # Padding
        "Line 1",  # Message line 1
        "Line 2",  # Message line 2
        "",  # Padding
        "**********",  # Bottom border
    ]
    expected = "\n".join(expected_lines)

    assert bordered_message == expected


@pytest.mark.unit
def test_compile_formatter(log_record: logging.LogRecord) -> None:
    """Test that compile_formatter returns a working formatter."""
    formatter = BorderFormatter(
        format="%(levelname)s: %(message)s", border_char="-", border_width=20, padding=0
    )

    compiled_formatter = formatter.compile_formatter()
    formatted_message = compiled_formatter.format(log_record)

    expected_lines = [
        "--------------------",  # Top border
        "INFO: Test message",  # Formatted message
        "--------------------",  # Bottom border
    ]
    expected = "\n".join(expected_lines)

    assert formatted_message == expected


@pytest.mark.unit
def test_formatter_with_logger() -> None:
    """Test the BorderFormatter with an actual logger."""
    # Create a string IO to capture log output
    log_output = io.StringIO()

    # Create a handler that writes to the string IO
    handler = logging.StreamHandler(log_output)

    # Create and configure the formatter
    formatter = BorderFormatter(
        format="%(levelname)s: %(message)s", border_char="=", border_width=30, padding=1
    )

    # Set the formatter on the handler
    handler.setFormatter(formatter.compile_formatter())

    # Create a logger and add the handler
    logger = logging.getLogger("test_logger")
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    # Log a message
    logger.info("Test log message")

    # Get the output
    output = log_output.getvalue()

    # Define the expected output
    expected_lines = [
        "==============================",  # Top border
        "",  # Padding
        "INFO: Test log message",  # Message
        "",  # Padding
        "==============================",  # Bottom border
    ]
    expected = "\n".join(expected_lines) + "\n"  # Logger adds newline at end

    assert output == expected


@pytest.mark.unit
@pytest.mark.parametrize(
    "border_char,border_width,padding,message",
    [
        ("-", 10, 0, "Test"),
        ("*", 15, 1, "Hello"),
        ("#", 20, 2, "Border"),
        ("=", 25, 0, "Multiple\nLines\nHere"),
    ],
)
def test_border_formatter_parametrized(
    border_char: str, border_width: int, padding: int, message: str
) -> None:
    """
    Test BorderFormatter with various configurations.

    Args:
        border_char: Character to use for border
        border_width: Width of the border
        padding: Number of empty lines between border and message
        message: Message to format
    """
    formatter = BorderFormatter(
        border_char=border_char, border_width=border_width, padding=padding
    )

    bordered_message = formatter._apply_border(message)

    # Verify top border
    lines = bordered_message.split("\n")
    assert lines[0] == border_char * border_width

    # Verify bottom border
    assert lines[-1] == border_char * border_width

    # Verify padding
    if padding > 0:
        for i in range(1, padding + 1):
            assert lines[i] == ""

        for i in range(len(lines) - padding - 1, len(lines) - 1):
            assert lines[i] == ""

    # Verify message is in the output
    for line in message.split("\n"):
        assert line in bordered_message


@pytest.mark.unit
def test_model_post_init() -> None:
    """Test that model_post_init properly sets up the message format."""
    formatter = BorderFormatter(format="%(levelname)s: %(message)s")

    # Check that message_format is set to the original format
    assert formatter.message_format == "%(levelname)s: %(message)s"
