import logging

import pytest

from swarmauri_standard.logger_formatters.HTMLFormatter import (
    HTMLFormatter,
    HTMLLoggingFormatter,
)


@pytest.fixture
def html_formatter():
    """
    Fixture that provides a default HTMLFormatter instance.
    """
    return HTMLFormatter()


@pytest.fixture
def log_record():
    """
    Fixture that provides a sample log record for testing.
    """
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test_file.py",
        lineno=42,
        msg="Test message",
        args=(),
        exc_info=None,
    )
    return record


@pytest.fixture
def log_record_with_exception():
    """
    Fixture that provides a sample log record with exception info.
    """
    try:
        raise ValueError("Test exception")
    except ValueError:
        import sys

        record = logging.LogRecord(
            name="test_logger",
            level=logging.ERROR,
            pathname="test_file.py",
            lineno=42,
            msg="Exception occurred",
            args=(),
            exc_info=sys.exc_info(),
        )
        return record


@pytest.mark.unit
def test_html_formatter_init():
    """
    Test that HTMLFormatter initializes with default values.
    """
    formatter = HTMLFormatter()

    assert formatter.include_timestamp is True
    assert formatter.date_format == "%Y-%m-%d %H:%M:%S"
    assert formatter.css_class == "log-entry"
    assert "DEBUG" in formatter.level_css_classes
    assert "INFO" in formatter.level_css_classes
    assert formatter.use_colors is True
    assert "ERROR" in formatter.level_colors
    assert formatter.include_line_breaks is True


@pytest.mark.unit
def test_escape_html():
    """
    Test that the escape_html method properly escapes HTML special characters.
    """
    formatter = HTMLFormatter()

    test_cases = [
        (
            "<script>alert('XSS')</script>",
            "&lt;script&gt;alert(&#x27;XSS&#x27;)&lt;/script&gt;",
        ),
        ("a & b", "a &amp; b"),
        ('quote "test"', "quote &quot;test&quot;"),
        (
            "'single'",
            "&#x27;single&#x27;",
        ),  # Single quotes are escaped by html.escape()
        ("<div>", "&lt;div&gt;"),
    ]

    for input_str, expected in test_cases:
        assert formatter.escape_html(input_str) == expected


@pytest.mark.unit
def test_compile_formatter(html_formatter):
    """
    Test that compile_formatter returns the correct formatter instance.
    """
    formatter = html_formatter.compile_formatter()

    assert isinstance(formatter, HTMLLoggingFormatter)
    assert formatter.config == html_formatter


@pytest.mark.unit
def test_html_logging_formatter_format_basic(html_formatter, log_record):
    """
    Test that HTMLLoggingFormatter correctly formats a basic log record.
    """
    formatter = HTMLLoggingFormatter(html_formatter)
    result = formatter.format(log_record)

    # Check basic structure
    assert '<div class="log-entry">' in result
    assert "</div>" in result

    # Check timestamp is included
    assert '<span class="log-timestamp">' in result

    # Check log level with styling
    assert f'<span class="{html_formatter.level_css_classes["INFO"]}"' in result
    assert 'style="color: ' in result
    assert "[INFO]</span>" in result

    # Check logger name
    assert '<span class="log-name">[test_logger]</span>' in result

    # Check message
    assert '<span class="log-message">Test message</span>' in result

    # Check no exception info
    assert '<pre class="log-exception">' not in result


@pytest.mark.unit
def test_html_logging_formatter_with_exception(
    html_formatter, log_record_with_exception
):
    """
    Test that HTMLLoggingFormatter correctly formats a log record with exception info.
    """
    formatter = HTMLLoggingFormatter(html_formatter)
    result = formatter.format(log_record_with_exception)

    # Check exception info is included
    assert '<pre class="log-exception">' in result
    assert "ValueError: Test exception" in result
    assert "<br>" in result  # Newlines should be converted to <br> tags


@pytest.mark.unit
def test_html_logging_formatter_without_timestamp():
    """
    Test that HTMLLoggingFormatter respects the include_timestamp setting.
    """
    formatter_config = HTMLFormatter(include_timestamp=False)
    formatter = HTMLLoggingFormatter(formatter_config)

    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test_file.py",
        lineno=42,
        msg="Test message",
        args=(),
        exc_info=None,
    )

    result = formatter.format(record)
    assert '<span class="log-timestamp">' not in result


@pytest.mark.unit
def test_html_logging_formatter_without_colors():
    """
    Test that HTMLLoggingFormatter respects the use_colors setting.
    """
    formatter_config = HTMLFormatter(use_colors=False)
    formatter = HTMLLoggingFormatter(formatter_config)

    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test_file.py",
        lineno=42,
        msg="Test message",
        args=(),
        exc_info=None,
    )

    result = formatter.format(record)
    assert 'style="color: ' not in result


@pytest.mark.unit
def test_html_logging_formatter_without_css_class():
    """
    Test that HTMLLoggingFormatter handles the case when css_class is None.
    """
    formatter_config = HTMLFormatter(css_class=None)
    formatter = HTMLLoggingFormatter(formatter_config)

    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test_file.py",
        lineno=42,
        msg="Test message",
        args=(),
        exc_info=None,
    )

    result = formatter.format(record)
    assert "<div >" in result  # No class attribute


@pytest.mark.unit
@pytest.mark.parametrize(
    "level,expected_class,expected_color",
    [
        (logging.DEBUG, "log-debug", "#888888"),
        (logging.INFO, "log-info", "#0000FF"),
        (logging.WARNING, "log-warning", "#FF8C00"),
        (logging.ERROR, "log-error", "#FF0000"),
        (logging.CRITICAL, "log-critical", "#8B0000"),
    ],
)
def test_html_logging_formatter_level_styling(level, expected_class, expected_color):
    """
    Test that HTMLLoggingFormatter applies correct styling for different log levels.
    """
    formatter_config = HTMLFormatter()
    formatter = HTMLLoggingFormatter(formatter_config)

    level_name = logging.getLevelName(level)
    record = logging.LogRecord(
        name="test_logger",
        level=level,
        pathname="test_file.py",
        lineno=42,
        msg="Test message",
        args=(),
        exc_info=None,
    )

    result = formatter.format(record)
    assert f'class="{expected_class}"' in result
    assert f'style="color: {expected_color}"' in result
    assert f"[{level_name}]</span>" in result


@pytest.mark.unit
def test_custom_date_format():
    """
    Test that HTMLLoggingFormatter respects the custom date_format setting.
    """
    custom_format = "%H:%M:%S"
    formatter_config = HTMLFormatter(date_format=custom_format)
    formatter = HTMLLoggingFormatter(formatter_config)

    # Create a log record with a fixed time
    import time

    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test_file.py",
        lineno=42,
        msg="Test message",
        args=(),
        exc_info=None,
    )

    # Manually set the created time for consistent testing
    record.created = time.mktime(
        time.strptime("2023-01-01 12:34:56", "%Y-%m-%d %H:%M:%S")
    )

    result = formatter.format(record)

    # The formatted time should be just the hours:minutes:seconds
    formatted_time = time.strftime(custom_format, time.localtime(record.created))
    assert formatted_time in result


@pytest.mark.unit
def test_custom_level_css_classes():
    """
    Test that HTMLLoggingFormatter respects custom level_css_classes.
    """
    custom_classes = {
        "DEBUG": "custom-debug",
        "INFO": "custom-info",
        "WARNING": "custom-warning",
        "ERROR": "custom-error",
        "CRITICAL": "custom-critical",
    }

    formatter_config = HTMLFormatter(level_css_classes=custom_classes)
    formatter = HTMLLoggingFormatter(formatter_config)

    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test_file.py",
        lineno=42,
        msg="Test message",
        args=(),
        exc_info=None,
    )

    result = formatter.format(record)
    assert 'class="custom-info"' in result


@pytest.mark.unit
def test_custom_level_colors():
    """
    Test that HTMLLoggingFormatter respects custom level_colors.
    """
    custom_colors = {
        "DEBUG": "#111111",
        "INFO": "#222222",
        "WARNING": "#333333",
        "ERROR": "#444444",
        "CRITICAL": "#555555",
    }

    formatter_config = HTMLFormatter(level_colors=custom_colors)
    formatter = HTMLLoggingFormatter(formatter_config)

    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test_file.py",
        lineno=42,
        msg="Test message",
        args=(),
        exc_info=None,
    )

    result = formatter.format(record)
    assert 'style="color: #222222"' in result
