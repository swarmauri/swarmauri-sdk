import importlib
import logging
from typing import Any

import pytest


@pytest.fixture
def init_module() -> Any:
    """Fixture to import the __init__.py module for testing."""
    module = importlib.import_module("swarmauri_middleware_auth")
    return module


@pytest.mark.i9n
def test_init_module(init_module: Any) -> None:
    """Test that the __init__.py module initializes correctly."""
    logging.debug("Starting test_init_module")

    # Check that the module was loaded successfully
    assert init_module is not None

    # Check that the AuthMiddleware class was imported
    assert hasattr(init_module, "AuthMiddleware")

    # Check that the version was set correctly
    assert hasattr(init_module, "__version__")
    assert isinstance(init_module.__version__, str)

    logging.debug("Completed test_init_module successfully")
