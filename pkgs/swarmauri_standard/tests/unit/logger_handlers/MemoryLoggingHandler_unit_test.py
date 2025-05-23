import logging
from unittest.mock import MagicMock, patch

import pytest
from swarmauri_base.logger_handlers.HandlerBase import HandlerBase

from swarmauri_standard.logger_handlers.MemoryLoggingHandler import MemoryLoggingHandler


@pytest.fixture
def target_handler():
    """
    Fixture that provides a mock target handler.

    Returns:
        MagicMock: A mock handler object.
    """
    mock_handler = MagicMock(spec=logging.Handler)
    mock_handler_base = MagicMock(spec=HandlerBase)
    mock_handler_base.compile_handler.return_value = mock_handler

    # Change from "MockHandlerBase" to "HandlerBase" for Pydantic validation
    mock_handler_base.type = "HandlerBase"
    mock_handler_base.model_dump = MagicMock(return_value={"type": "HandlerBase"})
    mock_handler_base.to_dict = MagicMock(return_value={"type": "HandlerBase"})

    return mock_handler_base


@pytest.fixture
def memory_handler(target_handler):
    """
    Fixture that provides a MemoryLoggingHandler instance with a mock target.

    Args:
        target_handler: The target handler fixture.

    Returns:
        MemoryLoggingHandler: An instance of MemoryLoggingHandler.
    """
    handler = MemoryLoggingHandler(
        capacity=10, flushLevel=logging.ERROR, target=target_handler
    )
    return handler


@pytest.mark.unit
def test_type():
    """Test that the handler has the correct type."""
    handler = MemoryLoggingHandler()
    assert handler.type == "MemoryLoggingHandler"


@pytest.mark.unit
def test_default_values():
    """Test that the handler has the expected default values."""
    handler = MemoryLoggingHandler()
    assert handler.capacity == 100
    assert handler.flushLevel == logging.ERROR
    assert handler.target is None


@pytest.mark.unit
def test_init_with_custom_values():
    """Test initializing the handler with custom values."""
    handler = MemoryLoggingHandler(
        capacity=200, flushLevel=logging.WARNING, target="some_target"
    )
    assert handler.capacity == 200
    assert handler.flushLevel == logging.WARNING
    assert handler.target == "some_target"


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
def test_compile_handler(target_handler):
    """Test that compile_handler creates a properly configured memory handler."""
    handler = MemoryLoggingHandler(
        capacity=10,
        flushLevel=logging.WARNING,
        target=target_handler,
        level=logging.INFO,
    )

    with patch(
        "swarmauri_standard.logger_handlers.MemoryLoggingHandler.MemoryHandler"
    ) as mock_memory_handler:
        mock_instance = MagicMock()
        mock_memory_handler.return_value = mock_instance

        result = handler.compile_handler()

        # Verify MemoryHandler was created with correct parameters
        mock_memory_handler.assert_called_once_with(
            capacity=10,
            flushLevel=logging.WARNING,
            target=target_handler.compile_handler(),
        )

        # Verify level was set
        mock_instance.setLevel.assert_called_once_with(logging.INFO)

        # Verify formatter was set
        mock_instance.setFormatter.assert_called_once()

        assert result == mock_instance


@pytest.mark.unit
def test_compile_handler_with_formatter():
    """Test that compile_handler sets the formatter correctly."""
    target_handler = MagicMock(spec=HandlerBase)
    target_handler.compile_handler.return_value = MagicMock(spec=logging.Handler)

    # Add these for Pydantic validation
    target_handler.type = "HandlerBase"
    target_handler.model_dump = MagicMock(return_value={"type": "HandlerBase"})

    # Update this section to properly mock FormatterBase
    from swarmauri_base.logger_formatters.FormatterBase import FormatterBase

    formatter = MagicMock(spec=FormatterBase)
    formatter.type = "FormatterBase"
    formatter.model_dump = MagicMock(return_value={"type": "FormatterBase"})
    formatter.compile_formatter.return_value = logging.Formatter(
        "%(levelname)s: %(message)s"
    )

    # Create the handler
    handler = MemoryLoggingHandler(target=target_handler, formatter=formatter)

    with patch(
        "swarmauri_standard.logger_handlers.MemoryLoggingHandler.MemoryHandler"
    ) as mock_memory_handler:
        mock_instance = MagicMock()
        mock_memory_handler.return_value = mock_instance

        handler.compile_handler()

        # Verify formatter was set from the provided formatter
        formatter.compile_formatter.assert_called_once()
        mock_instance.setFormatter.assert_called_once_with(
            formatter.compile_formatter.return_value
        )


@pytest.mark.unit
def test_compile_handler_with_string_formatter():
    """Test that compile_handler handles string formatters correctly."""
    target_handler = MagicMock(spec=HandlerBase)
    target_handler.compile_handler.return_value = MagicMock(spec=logging.Handler)

    target_handler.type = "HandlerBase"
    target_handler.model_dump = MagicMock(return_value={"type": "HandlerBase"})

    format_string = "%(levelname)s: %(message)s"
    handler = MemoryLoggingHandler(target=target_handler, formatter=format_string)

    with (
        patch(
            "swarmauri_standard.logger_handlers.MemoryLoggingHandler.MemoryHandler"
        ) as mock_memory_handler,
        patch("logging.Formatter") as mock_formatter,
    ):
        mock_instance = MagicMock()
        mock_memory_handler.return_value = mock_instance

        handler.compile_handler()

        # Verify Formatter was created with the format string
        mock_formatter.assert_called_with(format_string)
        mock_instance.setFormatter.assert_called_once()


@pytest.mark.unit
def test_flush(memory_handler):
    """Test that flush calls the underlying memory handler's flush method."""
    mock_memory_handler = MagicMock()
    memory_handler._memory_handler = mock_memory_handler

    memory_handler.flush()

    mock_memory_handler.flush.assert_called_once()


@pytest.mark.unit
def test_close(memory_handler):
    """Test that close calls close on both the memory handler and target handler."""
    mock_memory_handler = MagicMock()
    mock_target_handler = MagicMock()

    memory_handler._memory_handler = mock_memory_handler
    memory_handler._target_handler = mock_target_handler

    memory_handler.close()

    mock_memory_handler.close.assert_called_once()
    mock_target_handler.close.assert_called_once()


@pytest.mark.unit
def test_set_target(memory_handler):
    """Test that setTarget updates the target handler correctly."""
    mock_memory_handler = MagicMock()
    memory_handler._memory_handler = mock_memory_handler

    new_target = MagicMock(spec=logging.Handler)
    memory_handler.setTarget(new_target)

    mock_memory_handler.setTarget.assert_called_once_with(new_target)
    assert memory_handler._target_handler == new_target


@pytest.mark.unit
def test_to_dict(target_handler):
    """Test that to_dict returns the expected dictionary representation."""
    # Setup target handler's to_dict method
    target_handler.to_dict.return_value = {"type": "MockHandler"}

    handler = MemoryLoggingHandler(
        capacity=50, flushLevel=logging.DEBUG, target=target_handler, level=logging.INFO
    )

    result = handler.to_dict()

    assert result["type"] == "MemoryLoggingHandler"
    assert result["capacity"] == 50
    assert result["flushLevel"] == logging.DEBUG
    assert result["target"] == {"type": "MockHandler"}
    assert result["level"] == logging.INFO


@pytest.mark.unit
def test_to_dict_with_string_target():
    """Test that to_dict handles string targets correctly."""
    handler = MemoryLoggingHandler(target="string_target")

    result = handler.to_dict()

    assert result["target"] == "string_target"


@pytest.mark.parametrize(
    "capacity,flush_level",
    [(10, logging.DEBUG), (200, logging.WARNING), (500, logging.CRITICAL)],
)
@pytest.mark.unit
def test_parameterized_init(capacity, flush_level, target_handler):
    """Test initializing with different capacity and flush level values."""
    handler = MemoryLoggingHandler(
        capacity=capacity, flushLevel=flush_level, target=target_handler
    )

    assert handler.capacity == capacity
    assert handler.flushLevel == flush_level

    with patch(
        "swarmauri_standard.logger_handlers.MemoryLoggingHandler.MemoryHandler"
    ) as mock_memory_handler:
        mock_instance = MagicMock()
        mock_memory_handler.return_value = mock_instance

        handler.compile_handler()

        mock_memory_handler.assert_called_once_with(
            capacity=capacity,
            flushLevel=flush_level,
            target=target_handler.compile_handler(),
        )
