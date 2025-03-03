"""
Unit tests for LoggerMixin.

These tests validate the logger initialization and configuration for models that inherit
from LoggerMixin.
"""

import logging
import pytest
from swarmauri_base.LoggerMixin import LoggerMixin  # Adjust the import as needed


class DummyModel(LoggerMixin):
    """
    Dummy model for testing LoggerMixin.

    This model is used to verify that LoggerMixin correctly initializes a logger,
    using either the class-level default or a provided custom logger.

    Attributes:
        name (str): An example field.
    """

    name: str

@pytest.mark.xfail
def test_custom_logger_injection():
    """
    Test that a custom logger passed during initialization is used by DummyModel.

    This test confirms that when a custom logger is provided, LoggerMixin assigns it to the instance,
    preserving the custom settings.
    """
    custom_logger = logging.getLogger("CustomLogger")
    custom_logger.setLevel(logging.DEBUG)
    model = DummyModel(name="TestModel", logger=custom_logger)
    # Verify that the injected custom logger is used.
    assert model.logger.name == "CustomLogger", "Injected custom logger should be used."
    assert model.logger.level == logging.DEBUG, "Custom logger level should be DEBUG."
