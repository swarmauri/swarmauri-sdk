"""Tests for the package initializer module."""

import importlib
from importlib.util import module_from_spec

import pytest
from swarmauri_middleware_gzipcompression import __version__


@pytest.mark.i9n
def test_module_import() -> None:
    """Test that the module can be imported and loaded successfully."""
    # Load the module using importlib to test for any import errors
    spec = importlib.util.find_spec("swarmauri_middleware_gzipcompression")
    assert spec is not None, "Failed to find module specification"

    # Load the module from spec
    module = module_from_spec(spec)
    spec.loader.exec_module(module)

    # Verify that the module has the expected components
    assert hasattr(module, "__version__"), "Module does not have __version__ attribute"
    assert hasattr(module, "__all__"), "Module does not have __all__ attribute"


def test_gzipcompressionmiddleware_import() -> None:
    """Test that GzipCompressionMiddleware is properly imported."""
    from swarmauri_middleware_gzipcompression import GzipCompressionMiddleware

    assert GzipCompressionMiddleware is not None, (
        "GzipCompressionMiddleware not imported"
    )
    assert isinstance(GzipCompressionMiddleware, type), (
        "GzipCompressionMiddleware is not a class"
    )


@pytest.mark.i9n
def test_version() -> None:
    """Test that the version string is properly set."""
    assert isinstance(__version__, str), "__version__ is not a string"
    assert __version__ == "0.0.0", "Version string is default value"
