import pytest
import logging
import threading
import time
from queue import Queue
from typing import Any, List, Optional, Union
from unittest.mock import MagicMock, patch

from swarmauri_standard.logger_handlers.QueueLoggingHandler import QueueLoggingHandler
from swarmauri_base.logger_formatters.FormatterBase import FormatterBase


@pytest.fixture
def queue_handler():
    """
    Create a QueueLoggingHandler instance for testing.

    Returns:
        QueueLoggingHandler: A handler instance with default settings.
    """
    return QueueLoggingHandler()


@pytest.fixture
def custom_queue():
    """
    Create a custom queue for testing.

    Returns:
        Queue: A new queue instance.
    """
    return Queue()


@pytest.mark.unit
def test_initialization_default():
    """Test initialization with default parameters."""
    handler = QueueLoggingHandler()

    assert handler.type == "QueueLoggingHandler"
    assert isinstance(handler.queue, Queue)
    assert handler.level == logging.INFO
    assert handler.formatter is None
    assert handler.respect_handler_level is True


@pytest.mark.unit
def test_initialization_custom():
    """Test initialization with custom parameters."""
    custom_queue = Queue()
    mock_formatter = MagicMock(spec=FormatterBase)

    handler = QueueLoggingHandler(
        queue=custom_queue,
        level=logging.DEBUG,
        formatter=mock_formatter,
        respect_handler_level=False,
    )

    assert handler.queue is custom_queue
    assert handler.level == logging.DEBUG
    assert handler.formatter is mock_formatter
    assert handler.respect_handler_level is False


@pytest.mark.unit
def test_get_queue(queue_handler):
    """Test get_queue method returns the expected queue."""
    queue = queue_handler.get_queue()

    assert queue is queue_handler.queue
    assert isinstance(queue, Queue)


@pytest.mark.unit
def test_compile_handler_creates_handler_with_default_formatter(queue_handler):
    """Test compile_handler creates a handler with default formatter when none is provided."""
    handler = queue_handler.compile_handler()

    assert isinstance(handler, logging.handlers.QueueHandler)
    assert handler.level == logging.INFO
    assert isinstance(handler.formatter, logging.Formatter)
    assert handler.formatter._fmt == "[%(name)s][%(levelname)s] %(message)s"


@pytest.mark.unit
def test_compile_handler_with_string_formatter():
    """Test compile_handler with a string formatter."""
    format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    handler = QueueLoggingHandler(formatter=format_string)

    compiled_handler = handler.compile_handler()

    assert isinstance(compiled_handler.formatter, logging.Formatter)
    assert compiled_handler.formatter._fmt == format_string


@pytest.mark.unit
def test_compile_handler_with_formatter_object():
    """Test compile_handler with a formatter object."""
    mock_formatter = MagicMock(spec=FormatterBase)
    mock_compiled_formatter = MagicMock(spec=logging.Formatter)
    mock_formatter.compile_formatter.return_value = mock_compiled_formatter

    handler = QueueLoggingHandler(formatter=mock_formatter)
    compiled_handler = handler.compile_handler()

    mock_formatter.compile_formatter.assert_called_once()
    assert compiled_handler.formatter is mock_compiled_formatter


@pytest.mark.unit
def test_prepare_queue_listener():
    """Test prepare_queue_listener creates a QueueListener with provided handlers."""
    queue_handler = QueueLoggingHandler()
    mock_handlers = [MagicMock(spec=logging.Handler), MagicMock(spec=logging.Handler)]

    with patch("logging.handlers.QueueListener") as mock_queue_listener:
        queue_listener = queue_handler.prepare_queue_listener(mock_handlers)

        # Check that QueueListener was created with the right parameters
        mock_queue_listener.assert_called_once_with(
            queue_handler.queue, *mock_handlers, respect_handler_level=True
        )


@pytest.mark.unit
def test_respect_handler_level_true():
    """Test that handler level is respected when respect_handler_level is True."""
    handler = QueueLoggingHandler(level=logging.ERROR, respect_handler_level=True)
    compiled_handler = handler.compile_handler()

    # Create a logger and add our handler
    logger = logging.getLogger("test_respect_handler_level_true")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(compiled_handler)

    # Log messages at different levels
    logger.debug("Debug message")
    logger.info("Info message")
    logger.error("Error message")

    # Only ERROR level message should be in the queue
    assert handler.queue.qsize() == 1
    record = handler.queue.get()
    assert record.levelname == "ERROR"
    assert record.getMessage() == "Error message"


@pytest.mark.unit
def test_respect_handler_level_false():
    """
    Test that handler level is ignored when respect_handler_level is False.

    Note: This test is a bit tricky because the QueueHandler in the standard library
    always respects the handler level. Our custom implementation should override this.
    """
    handler = QueueLoggingHandler(level=logging.ERROR, respect_handler_level=False)

    # Directly test the CustomQueueHandler's emit method by mocking
    with patch("logging.handlers.QueueHandler.emit") as mock_emit:
        compiled_handler = handler.compile_handler()

        # Create a record with INFO level (below handler's ERROR level)
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Info message",
            args=(),
            exc_info=None,
        )

        # Emit the record
        compiled_handler.emit(record)

        # Since respect_handler_level is False, emit should be called
        # even though the record level is below the handler level
        mock_emit.assert_called_once()


@pytest.mark.unit
def test_integration_with_queue_listener():
    """Test integration with QueueListener for processing log records."""
    # Create a handler and a target handler to receive processed records
    queue_handler = QueueLoggingHandler()
    target_handler = MagicMock(spec=logging.Handler)

    # Create a queue listener with our target handler
    listener = queue_handler.prepare_queue_listener([target_handler])

    # Start the listener in a separate thread
    listener.start()

    try:
        # Create a logger and add our queue handler
        logger = logging.getLogger("test_integration")
        logger.setLevel(logging.DEBUG)
        logger.addHandler(queue_handler.compile_handler())

        # Log a message
        test_message = "Test integration message"
        logger.info(test_message)

        # Give the listener some time to process the message
        time.sleep(0.1)

        # Check that the target handler received the message
        target_handler.handle.assert_called()
        record = target_handler.handle.call_args[0][0]
        assert record.getMessage() == test_message
    finally:
        # Clean up
        listener.stop()


@pytest.mark.unit
def test_custom_queue():
    """Test that a custom queue can be provided and is used correctly."""
    custom_queue = Queue()
    handler = QueueLoggingHandler(queue=custom_queue)

    assert handler.queue is custom_queue

    # Test that logging actually uses this queue
    compiled_handler = handler.compile_handler()
    logger = logging.getLogger("test_custom_queue")
    logger.addHandler(compiled_handler)
    logger.setLevel(logging.INFO)

    test_message = "Test message for custom queue"
    logger.info(test_message)

    # Message should be in our custom queue
    assert not custom_queue.empty()
    record = custom_queue.get()
    assert record.getMessage() == test_message


@pytest.mark.unit
def test_model_serialization():
    """Test that the handler can be serialized and deserialized correctly."""
    # Create a handler with custom settings
    custom_queue = Queue()
    original_handler = QueueLoggingHandler(
        queue=custom_queue,
        level=logging.WARNING,
        formatter="%(levelname)s: %(message)s",
        respect_handler_level=False,
    )

    # Serialize to JSON
    json_data = original_handler.model_dump_json()

    # Deserialize from JSON
    deserialized_handler = QueueLoggingHandler.model_validate_json(json_data)

    # Check that properties were preserved (except for the queue which isn't serializable)
    assert deserialized_handler.type == original_handler.type
    assert deserialized_handler.level == original_handler.level
    assert deserialized_handler.formatter == original_handler.formatter
    assert (
        deserialized_handler.respect_handler_level
        == original_handler.respect_handler_level
    )
    assert isinstance(deserialized_handler.queue, Queue)  # A new queue is created
