import io
import logging

import pytest

from swarmauri_standard.logger_formatters.LoggerFormatter import LoggerFormatter
from swarmauri_standard.logger_handlers.MemoryLoggingHandler import MemoryLoggingHandler
from swarmauri_standard.logger_handlers.StreamLoggingHandler import StreamLoggingHandler


@pytest.fixture
def string_io():
    """Fixture providing a StringIO object for capturing output."""
    return io.StringIO()


@pytest.fixture
def target_handler(string_io):
    """
    Fixture that provides a real StreamLoggingHandler.

    Returns:
        StreamLoggingHandler: A real handler object.
    """
    # Create a real StreamLoggingHandler
    stream_handler = StreamLoggingHandler(
        level=logging.INFO, formatter="%(levelname)s: %(message)s", stream=string_io
    )
    return stream_handler


@pytest.fixture
def memory_handler(target_handler):
    """
    Fixture that provides a MemoryLoggingHandler instance with a real target.

    Args:
        target_handler: The target handler fixture.

    Returns:
        MemoryLoggingHandler: An instance of MemoryLoggingHandler.
    """
    handler = MemoryLoggingHandler(
        capacity=10, flushLevel=logging.ERROR, target=target_handler
    )
    return handler


@pytest.fixture
def logger_formatter():
    """Fixture providing a LoggerFormatter instance."""
    return LoggerFormatter()


@pytest.fixture
def custom_logger_formatter():
    """Fixture providing a customized LoggerFormatter instance."""
    return LoggerFormatter(
        include_timestamp=True, include_process=True, include_thread=True
    )


@pytest.mark.unit
def test_type(memory_handler):
    """Test that the handler has the correct type."""
    assert memory_handler.type == "MemoryLoggingHandler"


@pytest.mark.unit
def test_default_values(memory_handler):
    """Test that the handler has the expected default values."""
    assert memory_handler.capacity == 10
    assert memory_handler.flushLevel == logging.ERROR


@pytest.mark.unit
def test_init_with_custom_values(target_handler):
    """Test initializing the handler with custom values."""
    handler = MemoryLoggingHandler(
        capacity=200, flushLevel=logging.WARNING, target=target_handler
    )
    assert handler.capacity == 200
    assert handler.flushLevel == logging.WARNING
    assert handler.target == target_handler


@pytest.mark.unit
def test_compile_handler_no_target():
    """Test that compile_handler raises ValueError when no target is specified."""
    handler = MemoryLoggingHandler()
    with pytest.raises(ValueError, match="requires a target handler"):
        handler.compile_handler()


@pytest.mark.unit
def test_compile_handler_with_string_target():
    """Test that compile_handler raises ValueError when target is a string."""
    handler = MemoryLoggingHandler(target="some_target")
    with pytest.raises(ValueError, match="resolution by name"):
        handler.compile_handler()


@pytest.mark.unit
def test_compile_handler(target_handler, string_io):
    """Test that compile_handler creates a properly configured memory handler."""
    handler = MemoryLoggingHandler(
        capacity=10,
        flushLevel=logging.WARNING,
        target=target_handler,
        level=logging.INFO,
    )

    # Compile the handler
    result = handler.compile_handler()

    # Verify it's the right type
    assert isinstance(result, logging.handlers.MemoryHandler)

    # Verify capacity and flush level
    assert result.capacity == 10
    assert result.flushLevel == logging.WARNING

    # Verify the level was set
    assert result.level == logging.INFO

    # Create a logger to test it
    logger = logging.getLogger("test_compile_handler")
    logger.setLevel(logging.INFO)
    # Clear existing handlers
    for h in logger.handlers:
        logger.removeHandler(h)
    logger.addHandler(result)

    # Log a message below the flush level
    logger.info("Test info message")

    # Nothing should be in the output yet
    assert string_io.getvalue() == ""

    # Log a message at the flush level
    logger.warning("Test warning message")

    # Both messages should now be in the output
    output = string_io.getvalue()
    assert "INFO: Test info message" in output
    assert "WARNING: Test warning message" in output


@pytest.mark.unit
def test_compile_handler_with_formatter(string_io, logger_formatter):
    """Test that compile_handler sets the formatter correctly."""
    # Create the handler with LoggerFormatter
    target_handler = StreamLoggingHandler(
        level=logging.INFO,
        formatter=logger_formatter,
        stream=string_io,
    )

    handler = MemoryLoggingHandler(
        target=target_handler,
        formatter=logger_formatter,
        capacity=10,
        flushLevel=logging.WARNING,
    )

    # Compile the handler
    compiled_handler = handler.compile_handler()

    # Create a logger to test the formatter
    logger = logging.getLogger("test_formatter")
    logger.setLevel(logging.INFO)
    # Clear existing handlers
    for h in logger.handlers:
        logger.removeHandler(h)
    logger.addHandler(compiled_handler)

    # Log a message at the flush level to trigger immediate output
    logger.warning("Logger format test")

    # Verify the format matches LoggerFormatter's format
    output = string_io.getvalue()
    assert "[test_formatter] [WARNING] Logger format test" in output


@pytest.mark.unit
def test_compile_handler_with_custom_logger_formatter(
    target_handler, string_io, custom_logger_formatter
):
    """Test that compile_handler works with a custom LoggerFormatter."""
    target_handler = StreamLoggingHandler(
        level=logging.INFO,
        formatter=custom_logger_formatter,
        stream=string_io,
    )
    # Create the handler with a customized LoggerFormatter
    handler = MemoryLoggingHandler(
        target=target_handler,
        formatter=custom_logger_formatter,
        capacity=10,
        flushLevel=logging.WARNING,
    )

    # Compile the handler
    compiled_handler = handler.compile_handler()

    # Create a logger to test the formatter
    logger = logging.getLogger("test_custom_formatter")
    logger.setLevel(logging.INFO)
    # Clear existing handlers
    for h in logger.handlers:
        logger.removeHandler(h)
    logger.addHandler(compiled_handler)

    # Log a message at the flush level to trigger immediate output
    logger.warning("Custom logger format test")

    # Verify the format includes the custom elements
    output = string_io.getvalue()
    # Should have timestamp, name, level, process and thread IDs
    assert "[test_custom_formatter]" in output
    assert "[WARNING]" in output
    assert "Process:" in output
    assert "Thread:" in output
    assert "[test_custom_formatter]" in output


@pytest.mark.unit
def test_compile_handler_with_string_formatter(target_handler, string_io):
    """Test that compile_handler handles string formatters correctly."""
    target_handler.formatter = "STRING_FORMAT: %(message)s"

    handler = MemoryLoggingHandler(
        target=target_handler,
        capacity=10,
        flushLevel=logging.WARNING,
    )

    # Compile the handler
    compiled_handler = handler.compile_handler()

    # Create a logger to test the formatter
    logger = logging.getLogger("test_string_formatter")
    logger.setLevel(logging.INFO)
    # Clear existing handlers
    for h in logger.handlers:
        logger.removeHandler(h)
    logger.addHandler(compiled_handler)

    # Log a message at the flush level to trigger immediate output
    logger.warning("String format test")

    # Verify the string format was applied
    output = string_io.getvalue()
    assert "STRING_FORMAT: String format test" in output


@pytest.mark.unit
def test_flush(memory_handler, string_io):
    """Test that flush calls the underlying memory handler's flush method."""
    # Compile the handler
    compiled_handler = memory_handler.compile_handler()

    # Create a logger
    logger = logging.getLogger("test_flush")
    logger.setLevel(logging.INFO)
    # Clear existing handlers
    for h in logger.handlers:
        logger.removeHandler(h)
    logger.addHandler(compiled_handler)

    # Log some messages below flush level
    logger.info("First message")
    logger.info("Second message")

    # Verify nothing has been output yet
    assert string_io.getvalue() == ""

    # Manually flush the handler
    memory_handler.flush()

    # Verify messages were flushed
    output = string_io.getvalue()
    assert "INFO: First message" in output
    assert "INFO: Second message" in output


@pytest.mark.unit
def test_close(memory_handler, string_io):
    """Test that close calls close on both the memory handler and target handler."""
    # Compile the handler
    compiled_handler = memory_handler.compile_handler()

    # Create a logger
    logger = logging.getLogger("test_close")
    logger.setLevel(logging.INFO)
    # Clear existing handlers
    for h in logger.handlers:
        logger.removeHandler(h)
    logger.addHandler(compiled_handler)

    # Log a message
    logger.info("Message before close")

    # Manually flush first to avoid unexpected flush during close
    memory_handler.flush()

    # Clear the output after flush
    string_io.truncate(0)
    string_io.seek(0)

    # Close the handler
    memory_handler.close()

    # Verify nothing in output
    assert string_io.getvalue() == ""


@pytest.mark.unit
def test_set_target(memory_handler, string_io, logger_formatter):
    """Test that setTarget updates the target handler correctly."""
    # Compile the handler
    compiled_handler = memory_handler.compile_handler()

    # Create a logger
    logger = logging.getLogger("test_set_target")
    logger.setLevel(logging.INFO)
    # Clear existing handlers
    for h in logger.handlers:
        logger.removeHandler(h)
    logger.addHandler(compiled_handler)

    # Log a message
    logger.info("First message")

    # Create a new target handler with LoggerFormatter
    new_target_io = io.StringIO()
    new_target = StreamLoggingHandler(
        level=logging.INFO, formatter=logger_formatter, stream=new_target_io
    ).compile_handler()

    # Set new target
    memory_handler.setTarget(new_target)

    # Log another message
    logger.info("Second message")

    # Flush to the new target
    memory_handler.flush()

    # Check original target still has no output
    assert string_io.getvalue() == ""

    # Check new target has both messages with LoggerFormatter format
    output = new_target_io.getvalue()
    assert "[test_set_target] [INFO] First message" in output
    assert "[test_set_target] [INFO] Second message" in output


@pytest.mark.parametrize(
    "capacity,flush_level",
    [(10, logging.DEBUG), (200, logging.WARNING), (500, logging.CRITICAL)],
)
@pytest.mark.unit
def test_parameterized_init(capacity, flush_level, target_handler, string_io):
    """Test initializing with different capacity and flush level values."""
    handler = MemoryLoggingHandler(
        capacity=capacity, flushLevel=flush_level, target=target_handler
    )

    assert handler.capacity == capacity
    assert handler.flushLevel == flush_level

    # Compile the handler
    compiled_handler = handler.compile_handler()

    # Verify capacity and flush level were set correctly
    assert compiled_handler.capacity == capacity
    assert compiled_handler.flushLevel == flush_level

    # Create a logger to test with
    logger = logging.getLogger(f"test_param_{capacity}_{flush_level}")
    logger.setLevel(logging.DEBUG)  # Set to lowest level to test all cases
    # Clear existing handlers
    for h in logger.handlers:
        logger.removeHandler(h)
    logger.addHandler(compiled_handler)

    # Log messages at various levels
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")

    # Check if output appears based on flush level
    if flush_level <= logging.DEBUG:
        # Should have flushed on first message
        assert string_io.getvalue() != ""
    elif flush_level <= logging.INFO:
        # Should have flushed on second message
        assert "INFO: Info message" in string_io.getvalue()
    elif flush_level <= logging.WARNING:
        # Should have flushed on third message
        assert "WARNING: Warning message" in string_io.getvalue()
    else:
        # Should not have flushed yet
        assert string_io.getvalue() == ""

        # Manually flush to verify messages were buffered
        handler.flush()
        output = string_io.getvalue()
        assert "INFO: Info message" in output
        assert "WARNING: Warning message" in output


@pytest.mark.unit
def test_end_to_end_logging_with_real_handlers_and_formatter(
    memory_handler, string_io, logger_formatter
):
    """Test end-to-end logging with real handlers and LoggerFormatter."""
    # Create a new handler with LoggerFormatter
    handler_with_formatter = MemoryLoggingHandler(
        capacity=10,
        flushLevel=logging.ERROR,
        target=StreamLoggingHandler(
            level=logging.INFO, formatter=logger_formatter, stream=string_io
        ),
    )

    # Compile the handler
    compiled_handler = handler_with_formatter.compile_handler()

    # Create a logger and add the compiled handler
    logger = logging.getLogger("test_e2e_logger_formatted")
    logger.setLevel(logging.DEBUG)
    # Remove existing handlers to avoid interference
    for handler in logger.handlers:
        logger.removeHandler(handler)
    logger.addHandler(compiled_handler)

    # Log messages below flush level (ERROR)
    logger.debug("Debug message")
    logger.info("Info message 1")
    logger.warning("Warning message")

    # Check that nothing has been flushed yet
    assert string_io.getvalue() == ""

    # Log a message at flush level to trigger automatic flush
    logger.error("Error message that triggers flush")

    # Check output in the StringIO buffer has correct LoggerFormatter format
    output = string_io.getvalue()
    assert "[test_e2e_logger_formatted] [INFO] Info message 1" in output
    assert "[test_e2e_logger_formatted] [WARNING] Warning message" in output
    assert (
        "[test_e2e_logger_formatted] [ERROR] Error message that triggers flush"
        in output
    )
    # Debug message should be filtered out by the target handler's INFO level
    assert "Debug message" not in output


@pytest.mark.unit
def test_capacity_based_flush(target_handler, string_io):
    """Test that memory handler flushes when capacity is reached."""
    # Create a memory handler with small capacity
    small_capacity_handler = MemoryLoggingHandler(
        capacity=3,  # Only 3 records before automatic flush
        flushLevel=logging.ERROR,  # High flush level to ensure capacity triggers first
        target=target_handler,
    )

    # Compile the handler
    compiled_handler = small_capacity_handler.compile_handler()

    # Create a logger
    logger = logging.getLogger("test_capacity_logger")
    logger.setLevel(logging.INFO)
    # Remove existing handlers
    for handler in logger.handlers:
        logger.removeHandler(handler)
    logger.addHandler(compiled_handler)

    # Log enough messages to trigger capacity-based flush
    logger.info("Message 1")
    logger.info("Message 2")

    # Check that nothing has been flushed yet
    assert string_io.getvalue() == ""

    # This should trigger the capacity-based flush
    logger.info("Message 3")

    # Verify all messages were flushed
    output = string_io.getvalue()
    assert "INFO: Message 1" in output
    assert "INFO: Message 2" in output
    assert "INFO: Message 3" in output
