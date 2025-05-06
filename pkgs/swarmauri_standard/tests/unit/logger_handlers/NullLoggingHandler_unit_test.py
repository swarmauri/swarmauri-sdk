import pytest
import logging
from unittest.mock import patch, MagicMock
from swarmauri_standard.logger_handlers.NullLoggingHandler import NullLoggingHandler
from swarmauri_base.logger_handlers.HandlerBase import HandlerBase


@pytest.fixture
def null_handler():
    """
    Creates a NullLoggingHandler instance for testing.
    
    Returns:
        NullLoggingHandler: A configured null logging handler.
    """
    return NullLoggingHandler()


@pytest.mark.unit
def test_inheritance():
    """Tests that NullLoggingHandler properly inherits from HandlerBase."""
    assert issubclass(NullLoggingHandler, HandlerBase)


@pytest.mark.unit
def test_type_attribute():
    """Tests that the type attribute is correctly set to 'NullLoggingHandler'."""
    handler = NullLoggingHandler()
    assert handler.type == "NullLoggingHandler"


@pytest.mark.unit
def test_compile_handler_returns_null_handler(null_handler):
    """Tests that compile_handler returns a NullHandler instance."""
    handler = null_handler.compile_handler()
    assert isinstance(handler, logging.NullHandler)


@pytest.mark.unit
def test_compile_handler_sets_level(null_handler):
    """Tests that the compiled handler has the correct log level set."""
    # Default level should be WARNING
    handler = null_handler.compile_handler()
    assert handler.level == logging.WARNING
    
    # Test with a custom level
    null_handler.level = logging.ERROR
    handler = null_handler.compile_handler()
    assert handler.level == logging.ERROR


@pytest.mark.unit
@pytest.mark.parametrize("log_level", [
    logging.DEBUG,
    logging.INFO,
    logging.WARNING,
    logging.ERROR,
    logging.CRITICAL
])
def test_handler_with_different_levels(log_level):
    """Tests that the handler works with different logging levels."""
    handler = NullLoggingHandler(level=log_level)
    compiled_handler = handler.compile_handler()
    assert compiled_handler.level == log_level


@pytest.mark.unit
def test_handler_discards_messages():
    """Tests that the NullHandler actually discards log messages."""
    # Create a logger with our null handler
    logger = logging.getLogger("test_null_logger")
    logger.setLevel(logging.DEBUG)
    
    # Remove any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Add our null handler
    null_handler = NullLoggingHandler().compile_handler()
    logger.addHandler(null_handler)
    
    # Log a message - this should be silently discarded
    with patch('logging.NullHandler.handle') as mock_handle:
        logger.error("This message should be discarded")
        mock_handle.assert_called_once()


@pytest.mark.unit
def test_serialization():
    """Tests that the handler can be properly serialized and deserialized."""
    original = NullLoggingHandler(level=logging.INFO)
    json_data = original.model_dump_json()
    
    # Deserialize
    deserialized = NullLoggingHandler.model_validate_json(json_data)
    
    assert deserialized.type == original.type
    assert deserialized.level == original.level


@pytest.mark.unit
def test_component_registration():
    """Tests that the NullLoggingHandler is properly registered with ComponentBase."""
    from swarmauri_core.ComponentBase import ComponentBase
    
    # Get all registered types for HandlerBase
    registered_types = ComponentBase.get_registered_types(HandlerBase)
    
    # Check that NullLoggingHandler is in the registered types
    assert "NullLoggingHandler" in registered_types
    assert registered_types["NullLoggingHandler"] == NullLoggingHandler