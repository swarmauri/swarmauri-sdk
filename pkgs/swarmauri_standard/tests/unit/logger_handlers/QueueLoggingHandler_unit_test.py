import logging
import queue
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from swarmauri_base.logger_formatters.FormatterBase import FormatterBase

from swarmauri_standard.logger_handlers.QueueLoggingHandler import QueueLoggingHandler


@pytest.fixture
def queue_handler() -> QueueLoggingHandler:
    """
    Fixture that provides a basic QueueLoggingHandler instance.

    Returns:
        QueueLoggingHandler: An instance of QueueLoggingHandler with default settings.
    """
    return QueueLoggingHandler()


@pytest.fixture
def custom_queue() -> Any:
    """
    Fixture that provides a custom queue instance.

    Returns:
        Any: A queue instance for testing.
    """
    return queue.Queue()


@pytest.mark.unit
def test_init_default_queue():
    """
    Test that a QueueLoggingHandler creates a default queue when none is provided.
    """
    handler = QueueLoggingHandler()
    assert isinstance(handler.queue, queue.Queue)
    assert handler.type == "QueueLoggingHandler"
    assert handler.level == logging.INFO
    assert handler.formatter is None
    assert handler.respect_handler_level is True


@pytest.mark.unit
def test_init_custom_queue(custom_queue):
    """
    Test that a QueueLoggingHandler uses a provided queue.
    """
    handler = QueueLoggingHandler(queue=custom_queue)
    assert handler.queue is custom_queue


@pytest.mark.unit
def test_get_queue(queue_handler):
    """
    Test the get_queue method returns the handler's queue.
    """
    result = queue_handler.get_queue()
    assert result is queue_handler.queue


@pytest.mark.unit
def test_set_queue(queue_handler, custom_queue):
    """
    Test the set_queue method updates the handler's queue.
    """
    queue_handler.set_queue(custom_queue)
    assert queue_handler.queue is custom_queue


@pytest.mark.unit
def test_compile_handler_default_formatter(queue_handler):
    """
    Test compile_handler creates a QueueHandler with default formatter.
    """
    handler = queue_handler.compile_handler()

    assert isinstance(handler, logging.handlers.QueueHandler)
    assert handler.queue is queue_handler.queue
    assert handler.level == logging.INFO
    assert isinstance(handler.formatter, logging.Formatter)
    assert handler.formatter._fmt == "[%(name)s][%(levelname)s] %(message)s"
    assert handler.respect_handler_level is True


@pytest.mark.unit
def test_compile_handler_string_formatter():
    """
    Test compile_handler creates a QueueHandler with a string formatter.
    """
    format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    handler = QueueLoggingHandler(formatter=format_string)
    compiled = handler.compile_handler()

    assert isinstance(compiled, logging.handlers.QueueHandler)
    assert isinstance(compiled.formatter, logging.Formatter)
    assert compiled.formatter._fmt == format_string


@pytest.mark.unit
def test_compile_handler_formatter_object():
    """
    Test compile_handler creates a QueueHandler with a FormatterBase object.
    """
    mock_formatter = MagicMock(spec=FormatterBase)
    mock_formatter.type = "FormatterBase"
    mock_formatter.model_dump = MagicMock(return_value={"type": "FormatterBase"})
    mock_formatter.compile_formatter.return_value = logging.Formatter(
        "%(levelname)s: %(message)s"
    )

    handler = QueueLoggingHandler(formatter=mock_formatter)
    compiled = handler.compile_handler()

    assert isinstance(compiled, logging.handlers.QueueHandler)
    mock_formatter.compile_formatter.assert_called_once()
    assert compiled.formatter == mock_formatter.compile_formatter.return_value


@pytest.mark.unit
def test_compile_handler_custom_level():
    """
    Test compile_handler respects custom logging level.
    """
    handler = QueueLoggingHandler(level=logging.DEBUG)
    compiled = handler.compile_handler()

    assert compiled.level == logging.DEBUG


@pytest.mark.unit
def test_compile_handler_respect_handler_level():
    """
    Test compile_handler sets respect_handler_level property.
    """
    # Test with respect_handler_level=False
    handler = QueueLoggingHandler(respect_handler_level=False)
    compiled = handler.compile_handler()

    assert compiled.respect_handler_level is False


@pytest.mark.unit
def test_logging_with_handler():
    """
    Test that log records are properly enqueued when logging through the handler.
    """
    test_queue = queue.Queue()
    handler = QueueLoggingHandler(queue=test_queue)
    compiled_handler = handler.compile_handler()

    logger = logging.getLogger("test_logger")
    logger.setLevel(logging.INFO)
    logger.addHandler(compiled_handler)

    # Log a test message
    test_message = "Test log message"
    logger.info(test_message)

    # Verify the message was enqueued
    log_record = test_queue.get(block=False)

    # Change this line - get the basic message without formatting
    assert test_message in str(log_record.getMessage())
    assert log_record.levelno == logging.INFO
    assert log_record.name == "test_logger"


@pytest.mark.unit
def test_model_serialization():
    """
    Test that QueueLoggingHandler can be properly serialized and deserialized.
    """
    # Create a handler with custom settings
    original = QueueLoggingHandler(
        level=logging.DEBUG,
        formatter="%(levelname)s: %(message)s",
        respect_handler_level=False,
    )

    # Serialize to JSON
    json_data = original.model_dump_json()

    # Deserialize (we need to handle the queue separately as it's not serializable)
    with patch("queue.Queue"):
        deserialized = QueueLoggingHandler.model_validate_json(json_data)

    # Check that properties were preserved
    assert deserialized.type == "QueueLoggingHandler"
    assert deserialized.level == logging.DEBUG
    assert deserialized.formatter == "%(levelname)s: %(message)s"
    assert deserialized.respect_handler_level is False
