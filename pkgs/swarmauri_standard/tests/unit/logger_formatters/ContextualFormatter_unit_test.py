import logging

import pytest

from swarmauri_standard.logger_formatters.ContextualFormatter import (
    ContextualFormatter,
    ContextualFormatterImpl,
)


@pytest.fixture
def basic_formatter():
    """
    Create a basic ContextualFormatter with default settings.

    Returns:
        ContextualFormatter: A formatter instance with default settings
    """
    return ContextualFormatter()


@pytest.fixture
def custom_formatter():
    """
    Create a ContextualFormatter with custom settings.

    Returns:
        ContextualFormatter: A formatter instance with custom settings
    """
    return ContextualFormatter(
        format="%(levelname)s: %(message)s",
        date_format="%Y-%m-%d",
        context_keys=["session_id", "trace_id"],
        context_as_prefix=True,
        context_separator="|",
        context_prefix="<",
        context_suffix=">",
        context_item_format="{key}:{value}",
        include_empty_context=True,
    )


@pytest.mark.unit
def test_default_initialization():
    """Test that the formatter initializes with correct default values."""
    formatter = ContextualFormatter()

    assert formatter.format == "[%(name)s][%(levelname)s] %(message)s"
    assert formatter.date_format == "%Y-%m-%d %H:%M:%S"
    assert formatter.context_keys == ["request_id", "user_id", "correlation_id"]
    assert formatter.custom_context_keys == []
    assert formatter.context_as_prefix is False
    assert formatter.context_separator == " "
    assert formatter.context_prefix == "["
    assert formatter.context_suffix == "]"
    assert formatter.context_item_format == "{key}={value}"
    assert formatter.include_empty_context is False


@pytest.mark.unit
def test_custom_initialization():
    """Test that the formatter initializes with custom values."""
    formatter = ContextualFormatter(
        format="%(levelname)s: %(message)s",
        date_format="%Y-%m-%d",
        context_keys=["session_id", "trace_id"],
        context_as_prefix=True,
        context_separator="|",
        context_prefix="<",
        context_suffix=">",
        context_item_format="{key}:{value}",
        include_empty_context=True,
    )

    assert formatter.format == "%(levelname)s: %(message)s"
    assert formatter.date_format == "%Y-%m-%d"
    assert formatter.context_keys == ["session_id", "trace_id"]
    assert formatter.context_as_prefix is True
    assert formatter.context_separator == "|"
    assert formatter.context_prefix == "<"
    assert formatter.context_suffix == ">"
    assert formatter.context_item_format == "{key}:{value}"
    assert formatter.include_empty_context is True


@pytest.mark.unit
def test_add_context_key(basic_formatter):
    """Test adding a context key to the formatter."""
    # Add a new key
    basic_formatter.add_context_key("new_key")
    assert "new_key" in basic_formatter.custom_context_keys

    # Adding a duplicate key should not add it again
    basic_formatter.add_context_key("new_key")
    assert basic_formatter.custom_context_keys.count("new_key") == 1

    # Adding a key that's already in context_keys should not add it
    basic_formatter.add_context_key("request_id")
    assert "request_id" not in basic_formatter.custom_context_keys


@pytest.mark.unit
def test_compile_formatter(basic_formatter, custom_formatter):
    """Test that compile_formatter returns a properly configured ContextualFormatterImpl."""
    # Test with default formatter
    formatter_impl = basic_formatter.compile_formatter()
    assert isinstance(formatter_impl, ContextualFormatterImpl)
    assert (
        formatter_impl.context_keys
        == basic_formatter.context_keys + basic_formatter.custom_context_keys
    )
    assert formatter_impl.context_as_prefix == basic_formatter.context_as_prefix

    # Test with custom formatter
    formatter_impl = custom_formatter.compile_formatter()
    assert isinstance(formatter_impl, ContextualFormatterImpl)
    assert (
        formatter_impl.context_keys
        == custom_formatter.context_keys + custom_formatter.custom_context_keys
    )
    assert formatter_impl.context_as_prefix == custom_formatter.context_as_prefix
    assert formatter_impl.context_separator == custom_formatter.context_separator
    assert formatter_impl.context_prefix == custom_formatter.context_prefix
    assert formatter_impl.context_suffix == custom_formatter.context_suffix
    assert formatter_impl.context_item_format == custom_formatter.context_item_format
    assert (
        formatter_impl.include_empty_context == custom_formatter.include_empty_context
    )


@pytest.mark.unit
def test_contextual_formatter_impl_initialization():
    """Test initialization of the ContextualFormatterImpl class."""
    formatter = ContextualFormatterImpl(
        fmt="%(message)s",
        datefmt="%Y-%m-%d",
        context_keys=["key1", "key2"],
        context_as_prefix=True,
        context_separator="-",
        context_prefix="(",
        context_suffix=")",
        context_item_format="{key}:{value}",
        include_empty_context=True,
    )

    assert formatter._fmt == "%(message)s"
    assert formatter.datefmt == "%Y-%m-%d"
    assert formatter.context_keys == ["key1", "key2"]
    assert formatter.context_as_prefix is True
    assert formatter.context_separator == "-"
    assert formatter.context_prefix == "("
    assert formatter.context_suffix == ")"
    assert formatter.context_item_format == "{key}:{value}"
    assert formatter.include_empty_context is True


@pytest.mark.unit
def test_format_context_empty():
    """Test _format_context with empty context values."""
    formatter = ContextualFormatterImpl()
    result = formatter._format_context({})
    assert result == ""


@pytest.mark.unit
def test_format_context_with_values():
    """Test _format_context with context values."""
    # Test with default settings (key=value format)
    formatter = ContextualFormatterImpl()
    result = formatter._format_context({"request_id": "123", "user_id": "user1"})
    assert result == "[request_id=123 user_id=user1]"

    # Test with prefix mode
    formatter = ContextualFormatterImpl(context_as_prefix=True)
    result = formatter._format_context({"request_id": "123", "user_id": "user1"})
    assert result == "[123 user1]"

    # Test with custom settings
    formatter = ContextualFormatterImpl(
        context_as_prefix=False,
        context_separator="|",
        context_prefix="<",
        context_suffix=">",
        context_item_format="{key}:{value}",
    )
    result = formatter._format_context({"request_id": "123", "user_id": "user1"})
    assert result == "<request_id:123|user_id:user1>"


@pytest.mark.unit
def test_format_log_record_no_context():
    """Test formatting a log record with no context attributes."""
    formatter = ContextualFormatterImpl(fmt="%(levelname)s: %(message)s")

    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="Test message",
        args=(),
        exc_info=None,
    )

    result = formatter.format(record)
    assert result == "INFO: Test message"


@pytest.mark.unit
def test_format_log_record_with_context():
    """Test formatting a log record with context attributes."""
    formatter = ContextualFormatterImpl(fmt="%(levelname)s: %(message)s")

    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="Test message",
        args=(),
        exc_info=None,
    )

    # Add context attributes
    record.request_id = "req-123"
    record.user_id = "user-456"

    result = formatter.format(record)
    # Default behavior is to add after log level
    assert result == "INFO: [request_id=req-123 user_id=user-456] Test message"


@pytest.mark.unit
def test_format_log_record_with_context_as_prefix():
    """Test formatting a log record with context as prefix."""
    formatter = ContextualFormatterImpl(
        fmt="%(levelname)s: %(message)s", context_as_prefix=True
    )

    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="Test message",
        args=(),
        exc_info=None,
    )

    # Add context attributes
    record.request_id = "req-123"
    record.user_id = "user-456"

    result = formatter.format(record)
    assert result == "[req-123 user-456] INFO: Test message"


@pytest.mark.unit
def test_format_log_record_include_empty_context():
    """Test formatting a log record with include_empty_context=True."""
    formatter = ContextualFormatterImpl(
        fmt="%(levelname)s: %(message)s", include_empty_context=True
    )

    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="Test message",
        args=(),
        exc_info=None,
    )

    result = formatter.format(record)
    # Should include empty context brackets
    assert result == "INFO: [] Test message"


@pytest.mark.unit
def test_format_log_record_partial_context():
    """Test formatting a log record with only some context attributes present."""
    formatter = ContextualFormatterImpl(
        fmt="%(levelname)s: %(message)s",
        context_keys=["request_id", "user_id", "session_id"],
    )

    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="Test message",
        args=(),
        exc_info=None,
    )

    # Add only some context attributes
    record.request_id = "req-123"
    # user_id and session_id are missing

    result = formatter.format(record)
    assert result == "INFO: [request_id=req-123] Test message"


@pytest.mark.unit
def test_format_log_record_with_none_context_values():
    """Test formatting a log record with None context values."""
    formatter = ContextualFormatterImpl(fmt="%(levelname)s: %(message)s")

    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="Test message",
        args=(),
        exc_info=None,
    )

    # Add context attributes with None values
    record.request_id = "req-123"
    record.user_id = None  # This should be skipped

    result = formatter.format(record)
    assert result == "INFO: [request_id=req-123] Test message"
