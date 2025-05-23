import logging
from io import StringIO
from unittest.mock import MagicMock, patch

import pytest

from swarmauri_standard.logger_formatters.MultilineFormatter import (
    MultilineFormatter,
    _MultilineFormatterImpl,
)


@pytest.fixture
def basic_formatter():
    """
    Fixture providing a basic MultilineFormatter instance.

    Returns:
        MultilineFormatter: A basic MultilineFormatter instance
    """
    return MultilineFormatter()


@pytest.fixture
def custom_formatter():
    """
    Fixture providing a customized MultilineFormatter instance.

    Returns:
        MultilineFormatter: A customized MultilineFormatter instance
    """
    return MultilineFormatter(
        include_timestamp=True, prefix_subsequent_lines=True, indent_subsequent_lines=4
    )


@pytest.mark.unit
def test_multiline_formatter_init(basic_formatter):
    """
    Test the initialization of MultilineFormatter.

    Args:
        basic_formatter: Fixture providing a basic MultilineFormatter
    """
    assert basic_formatter.include_timestamp is True
    assert basic_formatter.prefix_subsequent_lines is True
    assert basic_formatter.indent_subsequent_lines == 0


@pytest.mark.unit
def test_multiline_formatter_post_init():
    """Test the post initialization of MultilineFormatter."""
    formatter = MultilineFormatter()
    # Check that format was properly built
    assert "%(asctime)s" in formatter.format
    assert "[%(name)s]" in formatter.format
    assert "[%(levelname)s]" in formatter.format
    assert "%(message)s" in formatter.format


@pytest.mark.unit
def test_multiline_formatter_without_timestamp():
    """Test MultilineFormatter configuration without timestamp."""
    formatter = MultilineFormatter(include_timestamp=False)
    # Check timestamp is not in format
    assert "%(asctime)s" not in formatter.format
    assert "[%(name)s]" in formatter.format


@pytest.mark.unit
def test_subsequent_line_prefix_calculation():
    """Test that the subsequent line prefix is calculated correctly."""
    formatter = MultilineFormatter()
    # Ensure the subsequent_line_prefix is set after initialization
    assert formatter.subsequent_line_prefix is not None
    assert len(formatter.subsequent_line_prefix) > 0


@pytest.mark.unit
def test_custom_subsequent_line_prefix():
    """Test using a custom subsequent line prefix."""
    custom_prefix = "    > "
    formatter = MultilineFormatter(subsequent_line_prefix=custom_prefix)
    assert formatter.subsequent_line_prefix == custom_prefix


@pytest.mark.unit
def test_compile_formatter(basic_formatter):
    """
    Test compiling the formatter into a logging.Formatter.

    Args:
        basic_formatter: Fixture providing a basic MultilineFormatter
    """
    formatter = basic_formatter.compile_formatter()
    assert isinstance(formatter, _MultilineFormatterImpl)
    assert formatter.prefix_subsequent_lines == basic_formatter.prefix_subsequent_lines
    assert formatter.subsequent_line_prefix == basic_formatter.subsequent_line_prefix
    assert formatter.indent_subsequent_lines == basic_formatter.indent_subsequent_lines


@pytest.mark.unit
def test_multiline_formatter_impl_single_line():
    """Test formatting a single line message."""
    formatter = _MultilineFormatterImpl(fmt="[%(levelname)s] %(message)s")
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="This is a single line message",
        args=(),
        exc_info=None,
    )

    formatted = formatter.format(record)
    assert formatted == "[INFO] This is a single line message"
    assert "\n" not in formatted


@pytest.mark.unit
def test_multiline_formatter_impl_multi_line():
    """Test formatting a multi-line message."""
    formatter = _MultilineFormatterImpl(
        fmt="[%(levelname)s] %(message)s", prefix_subsequent_lines=True
    )

    # Create a mock to get the prefix length
    mock_record = MagicMock()
    mock_record.getMessage.return_value = "First line\nSecond line"
    mock_record.levelname = "INFO"

    with patch.object(formatter, "formatMessage", return_value="[INFO] First line"):
        # Format will call formatMessage and then our custom logic
        formatter.format(mock_record)

    # Now test with a real record
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="First line\nSecond line\nThird line",
        args=(),
        exc_info=None,
    )

    formatted = formatter.format(record)
    lines = formatted.split("\n")

    assert len(lines) == 3
    assert lines[0] == "[INFO] First line"
    # Second and third lines should have some prefix
    assert lines[1].startswith(" ")
    assert lines[2].startswith(" ")
    assert "Second line" in lines[1]
    assert "Third line" in lines[2]


@pytest.mark.unit
def test_multiline_formatter_impl_with_indentation():
    """Test formatting with additional indentation for subsequent lines."""
    formatter = _MultilineFormatterImpl(
        fmt="[%(levelname)s] %(message)s",
        prefix_subsequent_lines=True,
        indent_subsequent_lines=4,
    )

    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="First line\nSecond line",
        args=(),
        exc_info=None,
    )

    formatted = formatter.format(record)
    lines = formatted.split("\n")

    # The second line should have the prefix plus 4 spaces
    assert "Second line" in lines[1]
    # Check that there are at least 4 spaces before "Second line"
    prefix_spaces = len(lines[1]) - len(lines[1].lstrip())
    assert prefix_spaces >= 4


@pytest.mark.unit
def test_multiline_formatter_impl_without_prefixing():
    """Test formatting multi-line message without prefixing subsequent lines."""
    formatter = _MultilineFormatterImpl(
        fmt="[%(levelname)s] %(message)s", prefix_subsequent_lines=False
    )

    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="First line\nSecond line",
        args=(),
        exc_info=None,
    )

    formatted = formatter.format(record)
    lines = formatted.split("\n")

    assert lines[0] == "[INFO] First line"
    assert lines[1] == "Second line"  # No prefix


@pytest.mark.unit
def test_multiline_formatter_impl_custom_prefix():
    """Test formatting with a custom prefix for subsequent lines."""
    custom_prefix = ">>> "
    formatter = _MultilineFormatterImpl(
        fmt="[%(levelname)s] %(message)s",
        prefix_subsequent_lines=True,
        subsequent_line_prefix=custom_prefix,
    )

    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="First line\nSecond line",
        args=(),
        exc_info=None,
    )

    formatted = formatter.format(record)
    lines = formatted.split("\n")

    assert lines[0] == "[INFO] First line"
    assert lines[1] == f"{custom_prefix}Second line"


@pytest.mark.unit
def test_integration_with_logger():
    """Test integrating the formatter with a logger."""
    formatter = MultilineFormatter(
        include_timestamp=False,  # Simpler for testing
        indent_subsequent_lines=2,
    ).compile_formatter()

    # Setup a logger with a string buffer
    log_buffer = StringIO()
    handler = logging.StreamHandler(log_buffer)
    handler.setFormatter(formatter)

    logger = logging.getLogger("test_logger")
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    # Log a multi-line message
    logger.info("This is line one\nThis is line two\nThis is line three")

    # Check the output
    output = log_buffer.getvalue()
    lines = output.strip().split("\n")

    assert len(lines) == 3
    assert "[test_logger]" in lines[0]
    assert "[INFO]" in lines[0]
    assert "This is line one" in lines[0]

    # Second and third lines should have proper formatting
    assert "This is line two" in lines[1]
    assert "This is line three" in lines[2]
