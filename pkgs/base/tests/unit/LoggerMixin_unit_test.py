"""
Unit tests for LoggerMixin.

These tests validate the logger initialization and configuration for models that
inherit from :class:`LoggerMixin`.
"""

import pytest
from swarmauri_base.LoggerMixin import LoggerMixin  # Adjust the import as needed


class DummyModel(LoggerMixin):
    """Dummy model for testing :class:`LoggerMixin`.

    This model verifies that :class:`LoggerMixin` leaves ``logger`` unset when no
    logger is supplied. A custom logger can be provided at instantiation or via
    ``default_logger``.

    Attributes:
        name (str): An example field.
    """

    name: str


@pytest.mark.unit
def test_default_logger_initialization():
    """
    Verify that no logger is created by default.

    If neither ``default_logger`` nor a custom logger is supplied,
    ``LoggerMixin`` leaves ``logger`` as ``None``.
    """
    model = DummyModel(name="TestModel")
    # Logger should remain unset.
    assert model.logger is None, "Logger should be null by default."
