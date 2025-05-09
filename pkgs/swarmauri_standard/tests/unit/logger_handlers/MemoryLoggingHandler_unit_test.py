import pytest
import logging
from unittest.mock import MagicMock, patch
from typing import Any

from swarmauri_standard.logger_handlers.MemoryLoggingHandler import MemoryLoggingHandler
from swarmauri_base.logger_handlers.HandlerBase import HandlerBase
from swarmauri_base.logger_formatters.FormatterBase import FormatterBase


@pytest.fixture
def mock_target_handler():
    """
    Create a mock target handler for testing.

    Returns:
        MagicMock: A mock handler object
    """
    mock_handler = MagicMock(spec=logging.Handler)
    mock_handler.compile_handler.return_value = mock_handler
    return mock_handler


@pytest.fixture
def memory_handler(mock_target_handler):
    """
    Create a basic MemoryLoggingHandler instance for testing.

    Args:
        mock_target_handler: The mock target handler fixture

    Returns:
        MemoryLoggingHandler: A configured memory handler for testing
    """
    return MemoryLoggingHandler(
        capacity=10, flushLevel=logging.ERROR, target=mock_target_handler
    )


@pytest.mark.unit
def test_memory_handler_type():
    """Test that the handler has the correct type."""
    assert MemoryLoggingHandler.type == "MemoryLoggingHandler"


@pytest.mark.unit
def test_memory_handler_default_values():
    """Test the default values of the MemoryLoggingHandler."""
    handler = MemoryLoggingHandler()
    assert handler.capacity == 100
    assert handler.flushLevel == logging.ERROR
    assert handler.target is None


@pytest.mark.unit
def test_memory_handler_custom_values():
    """Test setting custom values for the MemoryLoggingHandler."""
    handler = MemoryLoggingHandler(
        capacity=50, flushLevel=logging.WARNING, target="some_handler"
    )
    assert handler.capacity == 50
    assert handler.flushLevel == logging.WARNING
    assert handler.target == "some_handler"


@pytest.mark.unit
def test_compile_handler_no_target():
    """Test that compile_handler raises ValueError when no target is specified."""
    handler = MemoryLoggingHandler()
    with pytest.raises(
        ValueError, match="MemoryLoggingHandler requires a target handler"
    ):
        handler.compile_handler()


@pytest.mark.unit
def test_compile_handler_string_target():
    """Test that compile_handler raises ValueError for string targets (not implemented)."""
    handler = MemoryLoggingHandler(target="string_target")
    with pytest.raises(
        ValueError, match="String target handlers not implemented: string_target"
    ):
        handler.compile_handler()


@pytest.mark.unit
def test_compile_handler_invalid_target():
    """Test that compile_handler raises TypeError for invalid target types."""
    handler = MemoryLoggingHandler(target=123)  # type: ignore
    with pytest.raises(
        TypeError, match="Target must be a string or HandlerBase instance"
    ):
        handler.compile_handler()


@pytest.mark.unit
def test_compile_handler_with_handler_target(mock_target_handler):
    """
    Test compile_handler with a valid HandlerBase target.

    Args:
        mock_target_handler: The mock target handler fixture
    """
    handler = MemoryLoggingHandler(target=mock_target_handler)

    with patch("logging.handlers.MemoryHandler") as mock_memory_handler:
        mock_instance = MagicMock()
        mock_memory_handler.return_value = mock_instance

        result = handler.compile_handler()

        # Verify MemoryHandler was created with correct parameters
        mock_memory_handler.assert_called_once_with(
            capacity=100, flushLevel=logging.ERROR, target=mock_target_handler
        )

        # Verify level was set
        mock_instance.setLevel.assert_called_once()

        # Verify formatter was set
        mock_instance.setFormatter.assert_called_once()

        assert result == mock_instance


@pytest.mark.unit
def test_compile_handler_with_custom_formatter():
    """Test compile_handler with a custom formatter."""
    mock_formatter = MagicMock(spec=FormatterBase)
    mock_formatter.compile_formatter.return_value = logging.Formatter(
        "[TEST] %(message)s"
    )

    mock_target = MagicMock(spec=HandlerBase)
    mock_target.compile_handler.return_value = MagicMock(spec=logging.Handler)

    handler = MemoryLoggingHandler(target=mock_target, formatter=mock_formatter)

    with patch("logging.handlers.MemoryHandler") as mock_memory_handler:
        mock_instance = MagicMock()
        mock_memory_handler.return_value = mock_instance

        handler.compile_handler()

        # Verify formatter was created and set
        mock_formatter.compile_formatter.assert_called_once()
        mock_instance.setFormatter.assert_called_once()


@pytest.mark.unit
def test_compile_handler_with_string_formatter():
    """Test compile_handler with a string formatter."""
    mock_target = MagicMock(spec=HandlerBase)
    mock_target.compile_handler.return_value = MagicMock(spec=logging.Handler)

    handler = MemoryLoggingHandler(
        target=mock_target,
        formatter="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    with patch("logging.handlers.MemoryHandler") as mock_memory_handler:
        mock_instance = MagicMock()
        mock_memory_handler.return_value = mock_instance

        handler.compile_handler()

        # Verify formatter was set
        mock_instance.setFormatter.assert_called_once()


@pytest.mark.unit
def test_set_formatter():
    """Test the setFormatter method."""
    handler = MemoryLoggingHandler()
    formatter = logging.Formatter("%(message)s")

    # Before setting formatter
    assert handler.formatter is None

    handler.setFormatter(formatter)

    # After setting formatter
    assert handler.formatter == formatter


@pytest.mark.unit
def test_flush_method():
    """
    Test the flush method (which is a placeholder in the current implementation).

    This test just ensures the method exists and can be called without errors.
    """
    handler = MemoryLoggingHandler()
    # Should not raise an exception
    handler.flush()


@pytest.mark.unit
def test_close_method():
    """
    Test the close method (which is a placeholder in the current implementation).

    This test just ensures the method exists and can be called without errors.
    """
    handler = MemoryLoggingHandler()
    # Should not raise an exception
    handler.close()


@pytest.mark.unit
def test_serialization():
    """Test that the handler can be serialized and deserialized correctly."""
    handler = MemoryLoggingHandler(
        capacity=42, flushLevel=logging.WARNING, level=logging.DEBUG
    )

    # Serialize to JSON and back
    json_data = handler.model_dump_json()
    deserialized = MemoryLoggingHandler.model_validate_json(json_data)

    # Check that the deserialized object has the same attributes
    assert deserialized.capacity == 42
    assert deserialized.flushLevel == logging.WARNING
    assert deserialized.level == logging.DEBUG


@pytest.mark.unit
@pytest.mark.parametrize(
    "capacity,flush_level",
    [
        (10, logging.DEBUG),
        (100, logging.INFO),
        (1000, logging.WARNING),
        (5000, logging.ERROR),
        (10000, logging.CRITICAL),
    ],
)
def test_parametrized_initialization(capacity, flush_level, mock_target_handler):
    """
    Test initialization with different capacity and flush level values.

    Args:
        capacity: The buffer capacity to test
        flush_level: The flush level to test
        mock_target_handler: The mock target handler fixture
    """
    handler = MemoryLoggingHandler(
        capacity=capacity, flushLevel=flush_level, target=mock_target_handler
    )

    assert handler.capacity == capacity
    assert handler.flushLevel == flush_level

    with patch("logging.handlers.MemoryHandler") as mock_memory_handler:
        mock_instance = MagicMock()
        mock_memory_handler.return_value = mock_instance

        handler.compile_handler()

        # Verify MemoryHandler was created with correct parameters
        mock_memory_handler.assert_called_once_with(
            capacity=capacity, flushLevel=flush_level, target=mock_target_handler
        )
