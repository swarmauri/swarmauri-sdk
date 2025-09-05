import io
import logging
import sys
from unittest.mock import MagicMock

import pytest
from swarmauri_base.logger_formatters.FormatterBase import FormatterBase
from swarmauri_base.logger_handlers.HandlerBase import HandlerBase

from swarmauri_standard.logger_handlers.StreamLoggingHandler import StreamLoggingHandler


@pytest.fixture
def stream_handler():
    """
    Fixture to create a basic StreamLoggingHandler instance.

    Returns
    -------
    StreamLoggingHandler
        A basic StreamLoggingHandler instance.
    """
    return StreamLoggingHandler()


@pytest.mark.unit
def test_inheritance():
    """Test that StreamLoggingHandler inherits from HandlerBase."""
    assert issubclass(StreamLoggingHandler, HandlerBase)


@pytest.mark.unit
def test_default_values():
    """Test the default values of StreamLoggingHandler."""
    handler = StreamLoggingHandler()

    assert handler.type == "StreamLoggingHandler"
    assert handler.level == logging.INFO
    assert handler.formatter is None
    assert handler.stream is None


@pytest.mark.unit
@pytest.mark.parametrize(
    "level, formatter, stream",
    [
        (logging.DEBUG, "%(message)s", sys.stdout),
        (logging.ERROR, None, sys.stderr),
        (logging.WARNING, "%(levelname)s: %(message)s", None),
    ],
)
def test_initialization(level, formatter, stream):
    """
    Test initialization with different parameters.

    Parameters
    ----------
    level : int
        Logging level to test
    formatter : Optional[str]
        Formatter string to test
    stream : Optional[TextIO]
        Stream to test
    """
    handler = StreamLoggingHandler(level=level, formatter=formatter, stream=stream)

    assert handler.type == "StreamLoggingHandler"
    assert handler.level == level
    assert handler.formatter == formatter
    assert handler.stream == stream


@pytest.mark.unit
def test_compile_handler_with_default_values():
    """Test compiling a handler with default values."""
    handler = StreamLoggingHandler()
    compiled = handler.compile_handler()

    assert isinstance(compiled, logging.StreamHandler)
    assert compiled.level == logging.INFO
    assert isinstance(compiled.formatter, logging.Formatter)
    # Default stream should be sys.stderr
    assert compiled.stream == sys.stderr


@pytest.mark.unit
def test_compile_handler_with_custom_stream():
    """Test compiling a handler with a custom stream."""
    custom_stream = io.StringIO()
    handler = StreamLoggingHandler(stream=custom_stream)
    compiled = handler.compile_handler()

    assert compiled.stream == custom_stream


@pytest.mark.unit
def test_compile_handler_with_string_formatter():
    """Test compiling a handler with a string formatter."""
    format_string = "[%(name)s] %(levelname)s: %(message)s"
    handler = StreamLoggingHandler(formatter=format_string)
    compiled = handler.compile_handler()

    assert compiled.formatter._fmt == format_string


@pytest.mark.unit
def test_compile_handler_with_formatter_object():
    """Test compiling a handler with a FormatterBase object."""
    mock_formatter = MagicMock(spec=FormatterBase)
    mock_formatter.type = "FormatterBase"
    mock_formatter.model_dump = MagicMock(return_value={"type": "FormatterBase"})

    mock_formatter_instance = MagicMock(spec=logging.Formatter)
    mock_formatter.compile_formatter.return_value = mock_formatter_instance

    handler = StreamLoggingHandler(formatter=mock_formatter)
    compiled = handler.compile_handler()

    mock_formatter.compile_formatter.assert_called_once()
    assert compiled.formatter == mock_formatter_instance


@pytest.mark.unit
def test_functional_logging():
    """Test that the handler correctly logs messages to the stream."""
    # Create a StringIO object to capture the output
    stream = io.StringIO()
    handler = StreamLoggingHandler(stream=stream, level=logging.INFO)

    # Set up a logger with our handler
    logger = logging.getLogger("test_logger")
    logger.setLevel(logging.INFO)
    logger.addHandler(handler.compile_handler())

    # Clear any existing handlers
    logger.handlers = [handler.compile_handler()]

    # Log a message
    test_message = "This is a test message"
    logger.info(test_message)

    # Check that the message was logged to our stream
    output = stream.getvalue()
    assert test_message in output


@pytest.mark.unit
def test_serialization_deserialization():
    """Test that the handler can be serialized and deserialized correctly."""
    original = StreamLoggingHandler(
        level=logging.DEBUG, formatter="%(levelname)s: %(message)s", stream=None
    )

    # Serialize to JSON
    json_data = original.model_dump_json()

    # Deserialize from JSON
    deserialized = StreamLoggingHandler.model_validate_json(json_data)

    # Check that the deserialized object has the same attributes
    assert deserialized.type == original.type
    assert deserialized.level == original.level
    assert deserialized.formatter == original.formatter
    # Stream cannot be serialized/deserialized directly
    assert deserialized.stream is None


@pytest.mark.unit
def test_level_filtering():
    """Test that the handler correctly filters messages based on level."""
    stream = io.StringIO()
    handler = StreamLoggingHandler(stream=stream, level=logging.WARNING)

    # Set up a logger with our handler
    logger = logging.getLogger("test_filter_logger")
    logger.setLevel(logging.DEBUG)  # Allow all messages at the logger level

    # Clear any existing handlers and add our handler
    compiled_handler = handler.compile_handler()
    logger.handlers = [compiled_handler]

    # Log messages at different levels
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")

    # Check the output
    output = stream.getvalue()
    assert "Debug message" not in output
    assert "Info message" not in output
    assert "Warning message" in output
    assert "Error message" in output
