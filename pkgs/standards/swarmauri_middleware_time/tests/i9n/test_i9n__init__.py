"""Tests for the __init__.py module in swarmauri_middleware_time package."""
import pytest
from importlib import import_module
from importlib_metadata import PackageNotFoundError
import logging

from swarmauri_middleware_time import __version__ as package_version
from swarmauri_middleware_time import TimerMiddleware

@pytest.mark.i9n
def test_init_module():
    """Test that the __init__.py module initializes correctly."""
    # Import the module directly
    module = import_module("swarmauri_middleware_time")
    
    # Check that TimerMiddleware is in the module's namespace
    assert hasattr(module, "TimerMiddleware")
    
    # Verify the version string
    assert isinstance(package_version, str)
    assert len(package_version) > 0

@pytest.mark.i9n
def test_version_installed(mocker):
    """Test that the version is correctly retrieved when installed."""
    # Mock the version function to return a test version
    mock_version = mocker.patch(
        "importlib.metadata.version",
        return_value="1.2.3"
    )
    
    # Force reload the module to test version retrieval
    module = import_module("swarmauri_middleware_time")
    
    # Verify the version is set correctly
    assert package_version == "1.2.3"
    mock_version.assert_called_once_with("swarmauri_middleware_time")

@pytest.mark.i9n
def test_version_not_installed(mocker):
    """Test that the version defaults to 0.0.0 when not installed."""
    # Mock the import to raise PackageNotFoundError
    mocker.patch(
        "importlib.metadata",
        side_effect=PackageNotFoundError()
    )
    
    # Force reload the module
    module = import_module("swarmauri_middleware_time")
    
    # Verify the version is set to default
    assert package_version == "0.0.0"

@pytest.mark.i9n
def test_version_logging(mocker, caplog):
    """Test that appropriate logging occurs for version handling."""
    # Clear any existing logs
    caplog.clear()
    
    # Mock the import to raise PackageNotFoundError
    mocker.patch(
        "importlib.metadata",
        side_effect=PackageNotFoundError()
    )
    
    # Force reload the module
    import_module("swarmauri_middleware_time")
    
    # Verify the warning message was logged
    assert "Unable to find installed package version" in caplog.text
    assert "Defaulting to version: 0.0.0" in caplog.text
    assert caplog.record_tuples == [
        ("swarmauri_middleware_time", logging.WARNING, "Unable to find installed package version"),
        ("swarmauri_middleware_time", logging.WARNING, "Defaulting to version: 0.0.0")
    ]