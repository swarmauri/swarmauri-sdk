import io
import logging
from unittest.mock import patch

import pytest

from swarmauri_standard.logger_formatters.IndentedFormatter import IndentedFormatter


@pytest.fixture
def default_formatter():
    """
    Fixture providing a default IndentedFormatter instance.

    Returns:
        IndentedFormatter: A default instance of the IndentedFormatter.
    """
    return IndentedFormatter()


@pytest.fixture
def custom_formatter():
    """
    Fixture providing a customized IndentedFormatter instance.

    Returns:
        IndentedFormatter: A customized instance of the IndentedFormatter.
    """
    return IndentedFormatter(
        indent_width=2,
        indent_first_line=True,
        format="%(levelname)s - %(message)s",
        date_format="%Y-%m-%d %H:%M:%S",
    )


@pytest.mark.unit
def test_default_attributes():
    """Test the default attribute values of IndentedFormatter."""
    formatter = IndentedFormatter()
    assert formatter.indent_width == 4
    assert formatter.indent_first_line is False
    assert formatter.format == "[%(name)s][%(levelname)s] %(message)s"
    assert formatter.date_format is None


@pytest.mark.unit
@pytest.mark.parametrize(
    "indent_width,indent_first_line,format_str,date_format",
    [
        (2, True, "%(message)s", "%Y-%m-%d"),
        (8, False, "%(levelname)s: %(message)s", None),
        (0, True, "[%(name)s] %(message)s", "%H:%M:%S"),
    ],
)
def test_custom_attributes(indent_width, indent_first_line, format_str, date_format):
    """
    Test the initialization with custom attribute values.

    Args:
        indent_width: Number of spaces for indentation
        indent_first_line: Whether to indent the first line
        format_str: Log message format string
        date_format: Date format string
    """
    formatter = IndentedFormatter(
        indent_width=indent_width,
        indent_first_line=indent_first_line,
        format=format_str,
        date_format=date_format,
    )

    assert formatter.indent_width == indent_width
    assert formatter.indent_first_line == indent_first_line
    assert formatter.format == format_str
    assert formatter.date_format == date_format


@pytest.mark.unit
def test_negative_indent_width_validation():
    """Test that negative indent_width raises ValueError."""
    with pytest.raises(ValueError, match="indent_width must be a positive integer"):
        IndentedFormatter(indent_width=-1)


@pytest.mark.unit
def test_compile_formatter_returns_formatter(default_formatter):
    """Test that compile_formatter returns a logging.Formatter instance."""
    formatter = default_formatter.compile_formatter()
    assert isinstance(formatter, logging.Formatter)


@pytest.mark.unit
def test_single_line_no_indent_first_line(default_formatter):
    """Test formatting a single line message with no first line indentation."""
    # Create a log record with a single line message
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="This is a test message",
        args=(),
        exc_info=None,
    )

    # Get the formatter and format the record
    formatter = default_formatter.compile_formatter()
    formatted = formatter.format(record)

    # The message should not be indented (since indent_first_line is False)
    assert formatted == "[test_logger][INFO] This is a test message"


@pytest.mark.unit
def test_single_line_with_indent_first_line(custom_formatter):
    """Test formatting a single line message with first line indentation."""
    # Create a log record with a single line message
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="This is a test message",
        args=(),
        exc_info=None,
    )

    # Get the formatter and format the record
    formatter = custom_formatter.compile_formatter()
    formatted = formatter.format(record)

    # The message should be indented with 2 spaces (custom indent_width)
    assert formatted == "  INFO - This is a test message"


@pytest.mark.unit
def test_multi_line_message(default_formatter):
    """Test formatting a multi-line message."""
    # Create a log record with a multi-line message
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="Line 1\nLine 2\nLine 3",
        args=(),
        exc_info=None,
    )

    # Get the formatter and format the record
    formatter = default_formatter.compile_formatter()
    formatted = formatter.format(record)

    # The first line should not be indented, but subsequent lines should be
    expected = "[test_logger][INFO] Line 1\n    Line 2\n    Line 3"
    assert formatted == expected


@pytest.mark.unit
def test_multi_line_with_indent_first_line(custom_formatter):
    """Test formatting a multi-line message with first line indentation."""
    # Create a log record with a multi-line message
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="Line 1\nLine 2\nLine 3",
        args=(),
        exc_info=None,
    )

    # Get the formatter and format the record
    formatter = custom_formatter.compile_formatter()
    formatted = formatter.format(record)

    # All lines should be indented with 2 spaces
    expected = "  INFO - Line 1\n  Line 2\n  Line 3"
    assert formatted == expected


@pytest.mark.unit
def test_integration_with_logger():
    """Test the formatter in an actual logger setup."""
    # Create a string IO to capture log output
    log_capture = io.StringIO()
    handler = logging.StreamHandler(log_capture)

    # Create and configure formatter
    formatter = IndentedFormatter(
        indent_width=2, indent_first_line=False, format="[%(levelname)s] %(message)s"
    )
    handler.setFormatter(formatter.compile_formatter())

    # Set up logger
    logger = logging.getLogger("test_integration")
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.propagate = False  # Don't propagate to root logger

    # Log a multi-line message
    logger.info("First line\nSecond line\nThird line")

    # Check the output
    output = log_capture.getvalue()
    expected = "[INFO] First line\n  Second line\n  Third line\n"
    assert output == expected


@pytest.mark.unit
def test_model_post_init_called():
    """Test that model_post_init is called during initialization."""
    with patch.object(
        IndentedFormatter, "model_post_init", autospec=True
    ) as mock_post_init:
        formatter = IndentedFormatter(indent_width=3)
        mock_post_init.assert_called_once()
        assert formatter.indent_width == 3


@pytest.mark.unit
def test_zero_indent_width():
    """Test that zero indent_width is allowed and works correctly."""
    formatter = IndentedFormatter(indent_width=0)

    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="Line 1\nLine 2",
        args=(),
        exc_info=None,
    )

    log_formatter = formatter.compile_formatter()
    formatted = log_formatter.format(record)

    # With indent_width=0, no spaces should be added
    expected = "[test_logger][INFO] Line 1\nLine 2"
    assert formatted == expected
