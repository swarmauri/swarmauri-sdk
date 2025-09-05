import sys
from importlib import import_module

import pytest


@pytest.mark.i9n
def test_init_module():
    """Test that the __init__.py module initializes correctly."""
    # Import the module directly
    module = import_module("swarmauri_middleware_time")

    # Check that TimerMiddleware is in the module's namespace
    assert hasattr(module, "TimerMiddleware")

    # Verify the version string
    assert isinstance(module.__version__, str)
    assert len(module.__version__) > 0


@pytest.mark.i9n
def test_version_installed(mocker):
    """Test that the version is correctly retrieved when installed."""
    mock_version = mocker.patch("importlib.metadata.version", return_value="1.2.3")

    # Remove module from cache and reload
    if "swarmauri_middleware_time" in sys.modules:
        del sys.modules["swarmauri_middleware_time"]

    # Import fresh module
    module = import_module("swarmauri_middleware_time")

    # Verify the version is set correctly
    assert module.__version__ == "1.2.3"
    mock_version.assert_called_with("swarmauri_middleware_time")
