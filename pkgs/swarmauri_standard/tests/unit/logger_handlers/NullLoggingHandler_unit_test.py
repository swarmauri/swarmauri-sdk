import logging
from unittest.mock import patch

import pytest

from swarmauri_standard.logger_handlers.NullLoggingHandler import NullLoggingHandler


@pytest.mark.unit
def test_null_logging_handler_type():
    """
    Test that the NullLoggingHandler has the correct type attribute.
    """
    handler = NullLoggingHandler()
    assert handler.type == "NullLoggingHandler"


@pytest.mark.unit
def test_null_logging_handler_default_level():
    """
    Test that the NullLoggingHandler has the default logging level.
    """
    handler = NullLoggingHandler()
    assert handler.level == logging.INFO


@pytest.mark.unit
def test_null_logging_handler_custom_level():
    """
    Test that the NullLoggingHandler accepts a custom logging level.
    """
    handler = NullLoggingHandler(level=logging.ERROR)
    assert handler.level == logging.ERROR


@pytest.mark.unit
def test_compile_handler_returns_null_handler():
    """
    Test that compile_handler returns a NullHandler instance.
    """
    handler = NullLoggingHandler()
    compiled_handler = handler.compile_handler()

    assert isinstance(compiled_handler, logging.NullHandler)


@pytest.mark.unit
def test_compile_handler_sets_level():
    """
    Test that compile_handler sets the correct level on the NullHandler.
    """
    custom_level = logging.WARNING
    handler = NullLoggingHandler(level=custom_level)
    compiled_handler = handler.compile_handler()

    assert compiled_handler.level == custom_level


@pytest.mark.unit
def test_null_handler_discards_messages():
    """
    Test that the NullHandler actually discards log messages.
    """
    # Create a NullLoggingHandler
    handler = NullLoggingHandler()
    compiled_handler = handler.compile_handler()

    # Create a logger and add our handler
    logger = logging.getLogger("test_null_handler")
    logger.addHandler(compiled_handler)

    # The test passes if no exception is raised when logging
    # No assertion needed as NullHandler should silently discard the message
    logger.warning("This message should be discarded")


@pytest.mark.unit
def test_serialization_deserialization():
    """
    Test that the NullLoggingHandler can be serialized and deserialized correctly.
    """
    original_handler = NullLoggingHandler(level=logging.INFO)

    # Serialize to JSON
    json_data = original_handler.model_dump_json()

    # Deserialize from JSON
    deserialized_handler = NullLoggingHandler.model_validate_json(json_data)

    # Verify the deserialized handler has the same attributes
    assert deserialized_handler.type == original_handler.type
    assert deserialized_handler.level == original_handler.level


@pytest.mark.unit
@patch("logging.NullHandler")
def test_compile_handler_creates_null_handler(mock_null_handler):
    """
    Test that compile_handler creates a NullHandler.
    """
    # Setup
    handler = NullLoggingHandler(level=logging.DEBUG)

    # Execute
    handler.compile_handler()

    # Verify
    mock_null_handler.assert_called_once()
    mock_null_handler.return_value.setLevel.assert_called_once_with(logging.DEBUG)
