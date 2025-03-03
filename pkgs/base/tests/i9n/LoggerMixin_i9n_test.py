"""
Integration tests for LoggerMixin.

These tests simulate real-world usage by verifying that log messages are correctly emitted and
formatted when using a custom logging handler.
"""

import logging
import pytest
from swarmauri_base.LoggerMixin import LoggerMixin  # Adjust the import as needed


class DummyModel(LoggerMixin):
    """
    Dummy model for integration testing of LoggerMixin.

    This model demonstrates logging behavior in a simulated real-world scenario.

    Attributes:
        name (str): An example field.
    """

    name: str


class ListHandler(logging.Handler):
    """
    Custom logging handler that collects log messages in a list.

    This handler is used to capture log output during integration testing.

    Attributes:
        logs (list): A list storing formatted log messages.
    """

    def __init__(self, *args, **kwargs):
        """Initialize the ListHandler with an empty log list."""
        super().__init__(*args, **kwargs)
        self.logs = []

    def emit(self, record):
        """
        Emit a log record by formatting it and appending it to the logs list.

        Args:
            record (logging.LogRecord): The log record to be emitted.
        """
        msg = self.format(record)
        self.logs.append(msg)


@pytest.mark.i9n
def test_logging_output():
    """
    Test that log messages from DummyModel are correctly emitted using a custom ListHandler.

    This integration test replaces the default handlers with a ListHandler, logs a test message,
    and then verifies that the message was captured and formatted as expected.
    """
    # Create an instance of the custom list handler.
    list_handler = ListHandler()
    # Use logging's Formatter for the test instead of LoggerMixin.default_formatter.
    list_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))

    # Override the default handlers for DummyModel with the custom list handler.
    DummyModel.default_handlers = list_handler

    # Initialize the model, which triggers logger configuration.
    model = DummyModel(name="IntegrationTest")
    # Emit a test log message.
    model.logger.info("Integration test message")

    # Verify that the custom handler captured the log message.
    captured = any("Integration test message" in log for log in list_handler.logs)
    assert captured, "The custom log handler should capture the emitted log message."