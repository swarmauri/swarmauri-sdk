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


@pytest.mark.unit
def test_default_logger_initialization():
    """
    Test that the default logger is correctly initialized in DummyModel.

    When no logger is provided, DummyModel should create a logger using the class-level
    default logger (or fallback to the standard Python logger) with the expected name and level.
    """
    model = DummyModel(name="TestModel")
    # Assert that a logger instance exists.
    assert model.logger is not None, "Logger should be initialized by default."
    # Verify that the logger name is set to the model's class name.
    assert model.logger.name == "DummyModel", (
        "Logger name should match the model class name."
    )
    # Verify that the logger's level is set to the default log level.
    assert model.logger.level == logging.INFO, "Logger level should be INFO by default."


@pytest.mark.unit
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
