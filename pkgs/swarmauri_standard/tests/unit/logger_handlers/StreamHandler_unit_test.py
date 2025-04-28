import io
import logging
import sys
from unittest.mock import patch

import pytest

from swarmauri_standard.logger_handlers.StreamHandler import StreamHandler, StreamType


@pytest.fixture
def stream_handler():
    """Basic stream handler fixture with default settings."""
    return StreamHandler()


@pytest.mark.unit
def test_ubc_type(stream_handler):
    """Test that the component has the correct type."""
    assert stream_handler.type == "StreamHandler"


@pytest.mark.unit
def test_serialization(stream_handler):
    """Test that the component can be properly serialized and deserialized."""
    assert (
        stream_handler.id
        == StreamHandler.model_validate_json(stream_handler.model_dump_json()).id
    )


@pytest.mark.unit
def test_default_configuration(stream_handler):
    """Test that default configuration sets expected values."""
    assert stream_handler.stream_type == StreamType.STDOUT
    assert stream_handler.colorize is False
    assert stream_handler.level == logging.INFO  # Default from HandlerBase


@pytest.mark.unit
def test_custom_configuration():
    """Test initialization with custom configuration."""
    handler = StreamHandler(
        stream_type=StreamType.STDERR, colorize=True, level=logging.ERROR
    )

    assert handler.stream_type == StreamType.STDERR
    assert handler.colorize is True
    assert handler.level == logging.ERROR


@pytest.mark.unit
def test_compile_handler_stdout(stream_handler):
    """Test that the compile_handler method returns a properly configured handler for stdout."""
    compiled = stream_handler.compile_handler()

    assert isinstance(compiled, logging.StreamHandler)
    assert compiled.level == logging.INFO
    assert compiled.stream == sys.stdout


@pytest.mark.unit
def test_compile_handler_stderr():
    """Test that the compile_handler method returns a properly configured handler for stderr."""
    handler = StreamHandler(stream_type=StreamType.STDERR)
    compiled = handler.compile_handler()

    assert isinstance(compiled, logging.StreamHandler)
    assert compiled.stream == sys.stderr


@pytest.mark.unit
def test_default_formatter(stream_handler):
    """Test that the default formatter is correctly applied."""
    compiled = stream_handler.compile_handler()
    formatter = compiled.formatter

    assert isinstance(formatter, logging.Formatter)
    # Check that formatter contains expected patterns
    assert "[%(name)s]" in formatter._fmt
    assert "[%(levelname)s]" in formatter._fmt


@pytest.mark.unit
def test_colorized_formatter():
    """Test that the colorized formatter is correctly created and applied."""
    handler = StreamHandler(colorize=True)
    compiled = handler.compile_handler()

    # The formatter should be an instance of the inner ColorFormatter class
    formatter = compiled.formatter
    assert formatter.__class__.__name__ == "ColorFormatter"

    # Test formatting a log record to ensure colors are applied
    record = logging.LogRecord(
        name="test",
        level=logging.ERROR,
        pathname="",
        lineno=0,
        msg="Test error message",
        args=(),
        exc_info=None,
    )
    formatted = formatter.format(record)

    # Check that the formatting contains color codes
    assert "\033[31m" in formatted  # RED for ERROR
    assert "\033[0m" in formatted  # RESET


@pytest.mark.unit
def test_custom_string_formatter():
    """Test that a custom string formatter is correctly applied."""
    custom_format = "%(asctime)s - %(name)s - %(message)s"
    handler = StreamHandler(formatter=custom_format)
    compiled = handler.compile_handler()

    assert compiled.formatter._fmt == custom_format


@pytest.mark.unit
def test_integration_with_logger():
    """Test integration with Python's logging system."""
    # Create a string buffer to capture output
    buffer = io.StringIO()

    # Create a handler that writes to our buffer instead of stdout
    with patch("sys.stdout", buffer):
        handler = StreamHandler()
        compiled = handler.compile_handler()

        # Create a logger and add our handler
        logger = logging.getLogger("test_logger")
        logger.setLevel(logging.INFO)
        logger.addHandler(compiled)

        # Clear any existing handlers to avoid interference
        for h in logger.handlers[:-1]:
            logger.removeHandler(h)

        # Log a message
        test_message = "This is a test message"
        logger.info(test_message)

        # Check the output in our buffer
        output = buffer.getvalue()
        assert test_message in output
        assert "[test_logger]" in output
        assert "[INFO]" in output


@pytest.mark.unit
def test_repr(stream_handler):
    """Test the string representation of the handler."""
    repr_str = repr(stream_handler)
    assert "StreamHandler" in repr_str
    assert "stdout" in repr_str
    assert "INFO" in repr_str

    # Test with stderr and different level
    handler = StreamHandler(stream_type=StreamType.STDERR, level=logging.ERROR)
    repr_str = repr(handler)
    assert "stderr" in repr_str
    assert "ERROR" in repr_str


@pytest.mark.unit
def test_different_log_levels():
    """Test handling different log levels."""
    handler = StreamHandler(level=logging.WARNING)
    compiled = handler.compile_handler()

    # Create a string buffer to capture output
    buffer = io.StringIO()

    # Patch stdout to use our buffer
    with patch("sys.stdout", buffer):
        compiled.stream = buffer

        # Create and configure logger
        logger = logging.getLogger("level_test")
        logger.setLevel(logging.DEBUG)

        # Clear existing handlers
        for h in logger.handlers:
            logger.removeHandler(h)

        logger.addHandler(compiled)

        # Test messages at different levels
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")

        output = buffer.getvalue()

        # DEBUG and INFO should be filtered out
        assert "Debug message" not in output
        assert "Info message" not in output

        # WARNING and ERROR should be included
        assert "Warning message" in output
        assert "Error message" in output
