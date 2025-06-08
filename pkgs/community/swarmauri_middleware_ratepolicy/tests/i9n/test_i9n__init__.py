"""
Tests for the __init__.py module in the swarmauri_middleware_ratepolicy package.

This module ensures that the package initializer loads correctly and that all
public-facing symbols are properly exported.
"""

import pytest
import logging
from importlib import import_module

# Initialize the logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.mark.i9n
def test_module_import() -> None:
    """
    Test that the module can be imported without errors.

    This test ensures that the __init__.py file can be loaded and that no
    syntax errors or import issues exist in the module.
    """
    logger.info("Testing module import")
    try:
        import_module("swarmauri_middleware_ratepolicy")
    except ImportError as e:
        pytest.fail(f"Failed to import module: {e}")


@pytest.mark.i9n
def test_version() -> None:
    """
    Test that the __version__ string is properly set.

    This test verifies that the version string exists and is a valid string.
    """
    logger.info("Testing version")
    module = import_module("swarmauri_middleware_ratepolicy")
    assert hasattr(module, "__version__"), "__version__ not found"
    assert isinstance(module.__version__, str), "__version__ is not a string"


@pytest.mark.i9n
def test_exports() -> None:
    """
    Test that the expected symbols are exported in __all__.

    This test verifies that the __all__ variable contains the expected symbols
    and that they can be properly imported.
    """
    logger.info("Testing exports")
    module = import_module("swarmauri_middleware_ratepolicy")

    # Check __all__ exists
    assert hasattr(module, "__all__"), "__all__ not found"

    # Check RetryPolicyMiddleware is exported
    expected_exports = ["RetryPolicyMiddleware"]
    assert all(item in module.__all__ for item in expected_exports), (
        f"Not all expected exports found. Expected: {expected_exports}"
    )

    # Verify the class can be accessed
    cls = getattr(module, "RetryPolicyMiddleware")
    assert cls is not None, "Failed to get RetryPolicyMiddleware from module"


@pytest.mark.i9n
def test_all_variable() -> None:
    """
    Test that the __all__ variable contains the correct values.

    This test ensures that the __all__ variable is properly set and contains
    only the expected public symbols.
    """
    logger.info("Testing __all__ variable")
    module = import_module("swarmauri_middleware_ratepolicy")

    # Get the __all__ contents
    all_symbols = module.__all__

    # Expected symbols based on __init__.py
    expected_symbols = ["RetryPolicyMiddleware"]

    # Check that all expected symbols are present
    assert all(s in all_symbols for s in expected_symbols), (
        f"Not all expected symbols found in __all__. Expected: {expected_symbols}"
    )

    # Check that no unexpected symbols are present
    assert len(all_symbols) == len(expected_symbols), (
        f"Extra symbols found in __all__: {all_symbols}"
    )
