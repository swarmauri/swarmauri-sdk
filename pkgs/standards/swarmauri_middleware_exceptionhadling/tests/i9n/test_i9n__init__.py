import pytest
import logging
from importlib import import_module

@pytest.mark.i9n
def test_init_module():
    """Test the package initializer."""
    # Test that the module can be imported
    try:
        import_module("swarmauri_middleware_exceptionhadling")
    except ImportError as e:
        pytest.fail(f"Failed to import the module: {e}")

@pytest.mark.i9n
def test_init_contents():
    """Test the contents of the __init__.py file."""
    # Test that the __init__ exports the correct classes
    module = import_module("swarmauri_middleware_exceptionhadling")
    assert "ExceptionHandlingMiddleware" in module.__dict__, \
        "ExceptionHandlingMiddleware not exported in __init__"
    assert "version" in module.__dict__, \
        "Version not exported in __init__"
    assert "__all__" in module.__dict__, \
        "__all__ not defined in __init__"

@pytest.mark.i9n
def test_version():
    """Test that the version is correctly set."""
    module = import_module("swarmauri_middleware_exceptionhadling")
    assert isinstance(module.__version__, str), \
        "Version is not a string"
    assert len(module.__version__) > 0, \
        "Version string is empty"
    # If the package is installed, version should not be 0.0.0
    try:
        import pkg_resources
        pkg_resources.get_distribution("swarmauri_middleware_exceptionhadling")
        assert module.__version__ != "0.0.0", \
            "Version is 0.0.0 when package is installed"
    except pkg_resources.DistributionNotFound:
        pass  # Package is not installed, 0.0.0 version is acceptable

@pytest.mark.i9n
def test_all():
    """Test the __all__ variable."""
    module = import_module("swarmauri_middleware_exceptionhadling")
    assert isinstance(module.__all__, list), \
        "__all__ is not a list"
    assert "ExceptionHandlingMiddleware" in module.__all__, \
        "ExceptionHandlingMiddleware not in __all__"

# Setup logging for tests
logging.basicConfig(level=logging.DEBUG)