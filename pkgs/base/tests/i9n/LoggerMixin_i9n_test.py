import io
import logging
import pytest

from typing import Any
from swarmauri_base.LoggerMixin import LoggerMixin  # Adjust the import as needed
from swarmauri_base.logging.LoggerBase import LoggerBase
from swarmauri_base.logging.HandlerBase import HandlerBase
from swarmauri_base import register_type


class DummyModel(LoggerMixin):
    """Dummy model for integration testing of LoggerMixin.

    This model demonstrates logging behavior in a simulated real-world scenario.

    Attributes
    ----------
    name : str
        An example field.
    """

    name: str


@register_type()
class DummyHandler(HandlerBase):
    """Dummy handler model that wraps a custom StreamHandler.

    This dummy model implements the required compile_handler() method.
    """

    stream: Any = None
    level: int = logging.INFO
    format: str = "[%(name)s][%(levelname)s] %(message)s"

    def compile_handler(self) -> logging.Handler:
        """
        Compiles a logging handler using the specified level and format.
        In this example, a StreamHandler is created.
        """
        handler = logging.StreamHandler(self.stream)
        handler.setLevel(self.level)
        formatter = logging.Formatter(self.format)
        handler.setFormatter(formatter)
        return handler


@pytest.mark.i9n
def test_logging_output():
    """Test logging output using a custom StreamHandler provided via LoggerBase.handlers.

    This test creates an in-memory stream and a custom StreamHandler. It then wraps the handler
    in a dummy handler model and passes it via the LoggerBase constructor. When a log message is emitted,
    LoggerBase compiles the logger with the provided handler.
    """
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
