"""Integration tests for ``LoggerMixin`` behavior."""

import io
import logging
import pytest

from typing import Any
from swarmauri_base.LoggerMixin import LoggerMixin  # Adjust the import as needed
from swarmauri_base.loggers.LoggerBase import LoggerBase
from swarmauri_base.logger_handlers.HandlerBase import HandlerBase
from swarmauri_base import register_type


class DummyModel(LoggerMixin):
    """Model used to verify logging integration.

    Attributes:
        name (str): Example field to log.
    """

    name: str


@register_type()
class DummyHandler(HandlerBase):
    """Handler wrapper that builds a ``StreamHandler``."""

    stream: Any = None
    level: int = logging.INFO
    format: str = "[%(name)s][%(levelname)s] %(message)s"

    def compile_handler(self) -> logging.Handler:
        """Create and configure the logging handler."""
        handler = logging.StreamHandler(self.stream)
        handler.setLevel(self.level)
        formatter = logging.Formatter(self.format)
        handler.setFormatter(formatter)
        return handler


@pytest.mark.i9n
def test_logging_output():
    """Verify logging output using a custom handler."""
    # Create an in-memory stream
    log_stream = io.StringIO()

    # Provide the handler model in the LoggerBase constructor
    logger_base = LoggerBase(handlers=[DummyHandler(stream=log_stream)])

    # Assign our custom logger to the DummyModel's default_logger.
    DummyModel.default_logger = logger_base

    # Instantiate DummyModel which triggers logger initialization via model_post_init.
    model = DummyModel(name="IntegrationTest")

    # Emit a test log message.
    model.logger.info("Integration test message")

    # Get the stream's content.
    log_contents = log_stream.getvalue()

    # Assert that the log output contains the expected message.
    assert "INFO" in log_contents
    assert "Integration test message" in log_contents
