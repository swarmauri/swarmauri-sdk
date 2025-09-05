import logging

import pytest

from swarmauri_standard.logger_formatters.KeyValueFormatter import KeyValueFormatter


@pytest.fixture
def formatter():
    """
    Fixture that creates a KeyValueFormatter instance for testing.

    Returns:
        KeyValueFormatter: A newly created KeyValueFormatter instance
    """
    return KeyValueFormatter()


@pytest.mark.unit
def test_default_attributes():
    """
    Test that the default attributes are set correctly.
    """
    formatter = KeyValueFormatter()
    assert formatter.key_value_separator == "="
    assert formatter.pair_delimiter == " "
    assert formatter.include_extra is False
    assert formatter.fields == ["levelname", "name", "message"]
    assert formatter.format == "%(message)s"
    assert formatter.date_format == "%Y-%m-%d %H:%M:%S"


@pytest.mark.unit
def test_model_post_init():
    """
    Test that model_post_init sets the format attribute correctly.
    """
    formatter = KeyValueFormatter()
    formatter.model_post_init()
    assert formatter.format == "%(message)s"


@pytest.mark.unit
def test_compile_formatter(formatter):
    """
    Test that compile_formatter returns a logging.Formatter with the format method overridden.
    """
    log_formatter = formatter.compile_formatter()
    assert isinstance(log_formatter, logging.Formatter)
    assert log_formatter.format != logging.Formatter.format


@pytest.mark.unit
@pytest.mark.parametrize(
    "fields,expected_parts",
    [
        (
            ["levelname", "name", "message"],
            ["levelname=INFO", "name=test_logger", "message=Test message"],
        ),
        (["message", "name"], ["message=Test message", "name=test_logger"]),
        (["levelname"], ["levelname=INFO"]),
    ],
)
def test_format_record_with_different_fields(fields, expected_parts):
    """
    Test that format_record correctly formats log records with different field configurations.

    Args:
        fields: List of fields to include in the formatter
        expected_parts: Expected parts in the formatted output
    """
    formatter = KeyValueFormatter(fields=fields)

    # Create a log record
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test_path",
        lineno=10,
        msg="Test message",
        args=(),
        exc_info=None,
    )

    formatted = formatter.format_record(record)

    # Check that all expected parts are in the output
    for part in expected_parts:
        assert part in formatted

    # Check that the parts are joined with the correct delimiter
    assert formatted == formatter.pair_delimiter.join(expected_parts)


@pytest.mark.unit
def test_format_record_with_extra_attributes():
    """
    Test that format_record includes extra attributes when include_extra is True.
    """
    formatter = KeyValueFormatter(include_extra=True)

    # Create a log record with extra attributes
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test_path",
        lineno=10,
        msg="Test message",
        args=(),
        exc_info=None,
    )

    # Add extra attributes
    record.extra = {"custom_field": "custom_value"}
    record.another_custom_field = "another_value"

    formatted = formatter.format_record(record)

    # Check that standard fields are included
    assert "levelname=INFO" in formatted
    assert "name=test_logger" in formatted
    assert "message=Test message" in formatted

    # Check that extra attributes are included
    assert "custom_field=custom_value" in formatted
    assert "another_custom_field=another_value" in formatted


@pytest.mark.unit
def test_format_record_without_extra_attributes():
    """
    Test that format_record excludes extra attributes when include_extra is False.
    """
    formatter = KeyValueFormatter(include_extra=False)

    # Create a log record with extra attributes
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test_path",
        lineno=10,
        msg="Test message",
        args=(),
        exc_info=None,
    )

    # Add extra attributes
    record.extra = {"custom_field": "custom_value"}
    record.another_custom_field = "another_value"

    formatted = formatter.format_record(record)

    # Check that standard fields are included
    assert "levelname=INFO" in formatted
    assert "name=test_logger" in formatted
    assert "message=Test message" in formatted

    # Check that extra attributes are not included
    assert "custom_field=custom_value" not in formatted
    assert "another_custom_field=another_value" not in formatted


@pytest.mark.unit
def test_format_record_with_custom_separators():
    """
    Test that format_record uses the custom separators correctly.
    """
    formatter = KeyValueFormatter(key_value_separator=":", pair_delimiter="|")

    # Create a log record
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test_path",
        lineno=10,
        msg="Test message",
        args=(),
        exc_info=None,
    )

    formatted = formatter.format_record(record)

    # Check that the custom separators are used
    assert "levelname:INFO" in formatted
    assert "name:test_logger" in formatted
    assert "message:Test message" in formatted
    assert "|" in formatted


@pytest.mark.unit
def test_format_record_with_missing_field():
    """
    Test that format_record handles missing fields gracefully.
    """
    formatter = KeyValueFormatter(
        fields=["levelname", "name", "message", "nonexistent_field"]
    )

    # Create a log record
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test_path",
        lineno=10,
        msg="Test message",
        args=(),
        exc_info=None,
    )

    formatted = formatter.format_record(record)

    # Check that standard fields are included
    assert "levelname=INFO" in formatted
    assert "name=test_logger" in formatted
    assert "message=Test message" in formatted

    # Check that the nonexistent field is not included
    assert "nonexistent_field" not in formatted


@pytest.mark.unit
def test_format_record_with_message_formatting():
    """
    Test that format_record correctly applies message formatting.
    """
    formatter = KeyValueFormatter()

    # Create a log record with formatting
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test_path",
        lineno=10,
        msg="Test message with %s",
        args=("formatting",),
        exc_info=None,
    )

    formatted = formatter.format_record(record)

    # Check that the message is formatted correctly
    assert "message=Test message with formatting" in formatted
