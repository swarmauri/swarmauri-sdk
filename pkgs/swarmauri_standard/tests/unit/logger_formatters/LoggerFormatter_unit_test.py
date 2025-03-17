import logging
import pytest
from swarmauri_standard.logger_formatters.LoggerFormatter import LoggerFormatter


@pytest.fixture
def logger_formatter():
    return LoggerFormatter()


@pytest.mark.unit
def test_ubc_type(logger_formatter):
    assert logger_formatter.type == "LoggerFormatter"


@pytest.mark.unit
def test_serialization(logger_formatter):
    assert (
        logger_formatter.id
        == LoggerFormatter.model_validate_json(logger_formatter.model_dump_json()).id
    )


@pytest.mark.unit
def test_logger_formatter_default_config(logger_formatter):
    """Test LoggerFormatter with default configuration."""

    compiled_formatter = logger_formatter.compile_formatter()

    assert isinstance(compiled_formatter, logging.Formatter)

    assert "%(message)s" in logger_formatter.format
    assert "[%(name)s]" in logger_formatter.format
    assert "[%(levelname)s]" in logger_formatter.format

    assert "%(asctime)s" not in logger_formatter.format
    assert "Process:%(process)d" not in logger_formatter.format
    assert "Thread:%(thread)d" not in logger_formatter.format


@pytest.mark.unit
def test_logger_formatter_custom_config():
    """Test LoggerFormatter with custom configuration."""
    formatter = LoggerFormatter(
        include_timestamp=True, include_process=True, include_thread=True
    )

    formatter.compile_formatter()

    # Check format string based on configuration
    assert "%(asctime)s" in formatter.format
    assert "[%(name)s]" in formatter.format
    assert "[%(levelname)s]" in formatter.format
    assert "Process:%(process)d" in formatter.format
    assert "Thread:%(thread)d" in formatter.format
