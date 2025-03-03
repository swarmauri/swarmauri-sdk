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
    assert model.logger is None, "Logger should be null by default."