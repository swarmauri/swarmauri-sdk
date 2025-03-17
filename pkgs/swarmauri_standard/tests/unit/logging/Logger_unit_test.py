import logging
import io
import pytest
from swarmauri_standard.logging.Logger import Logger
from swarmauri_base.logger_handler.HandlerBase import HandlerBase
from swarmauri_standard.logger_formatters.LoggerFormatter import LoggerFormatter


@pytest.mark.unit
def test_ubc_type():
    assert Logger().type == "Logger"


@pytest.mark.unit
def test_serialization():
    logger = Logger()
    assert logger.id == Logger.model_validate_json(logger.model_dump_json()).id


@pytest.mark.unit
def test_logger_default_configuration():
    """Test Logger with default configuration."""
    # Create a logger with default settings
    logger = Logger(name="test_default")

    # Verify logger properties
    assert logger.name == "test_default"
    assert logger.default_level == logging.INFO
    assert isinstance(logger.logger, logging.Logger)

    # Check that at least one handler is attached
    assert len(logger.logger.handlers) > 0


@pytest.mark.unit
def test_logger_with_custom_level():
    """Test Logger with custom logging level."""
    # Create a logger with DEBUG level
    logger = Logger(name="test_level", default_level=logging.DEBUG)

    # Verify the level is set correctly
    assert logger.default_level == logging.DEBUG
    assert logger.logger.level == logging.DEBUG


@pytest.mark.unit
def test_logger_with_custom_handler():
    """Test Logger with a custom handler."""
    # Create a handler
    handler = HandlerBase(level=logging.INFO)

    # Create a logger with the custom handler
    logger = Logger(name="test_handler", handlers=[handler])

    # Get the actual handler from the logger
    actual_handler = logger.logger.handlers[0]

    # Verify the handler is attached
    assert len(logger.logger.handlers) == 1
    assert actual_handler.level == logging.INFO


@pytest.mark.unit
def test_logger_logging_functionality():
    """Test that the logger actually logs messages correctly."""
    # Create a stream to capture log output
    stream = io.StringIO()

    # Create a handler that logs to our stream
    handler = logging.StreamHandler(stream)
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))

    # Create our logger with this handler
    logger = Logger(name="test_logging")

    # Replace the default handlers with our test handler
    logger.logger.handlers = [handler]

    # Log some messages
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")

    # Get the output
    output = stream.getvalue()

    # Verify the messages were logged
    assert "INFO: Info message" in output
    assert "WARNING: Warning message" in output
    assert "ERROR: Error message" in output


@pytest.mark.unit
def test_logger_with_formatter():
    """Test Logger with a custom formatter."""
    # Create a formatter
    formatter = LoggerFormatter(
        include_timestamp=False, include_process=True, include_thread=True
    )

    # Create a stream to capture log output
    stream = io.StringIO()

    # Create a handler with our formatter
    custom_handler = HandlerBase(level=logging.INFO, formatter=formatter)

    # Create a logger with the custom handler
    logger = Logger(name="test_formatter", handlers=[custom_handler])

    # Replace the stream in the actual handler
    actual_handler = logger.logger.handlers[0]
    actual_handler.stream = stream

    # Log a message
    logger.info("Test with formatter")

    # Get the output
    output = stream.getvalue()

    # Verify the format includes process and thread but not timestamp
    assert "[test_formatter]" in output
    assert "[INFO]" in output
    assert "Process:" in output
    assert "Thread:" in output
    assert "Test with formatter" in output
