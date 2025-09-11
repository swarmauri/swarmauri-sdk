import logging
from importlib import import_module

import pytest


@pytest.mark.i9n
def test_init_module_loads():
    """Test that the __init__ module loads correctly."""
    logging.debug("Testing __init__ module load")
    mod = import_module("swarmauri_middleware_ratelimit")
    assert hasattr(mod, "__version__"), "Module should have __version__ attribute"
    assert hasattr(mod, "__all__"), "Module should have __all__ attribute"
    assert mod.__all__ == ["RateLimitMiddleware"], (
        "__all__ should contain RateLimitMiddleware"
    )
    logging.debug("Successfully loaded __init__ module")


@pytest.mark.i9n
def test_version():
    """Test that the version string is correctly set."""
    logging.debug("Testing version string")
    mod = import_module("swarmauri_middleware_ratelimit")
    version = mod.__version__
    assert isinstance(version, str), "__version__ should be a string"
    assert len(version.strip()) > 0, "__version__ should not be empty"


@pytest.mark.i9n
def test_rate_limit_middleware_import():
    """Test that RateLimitMiddleware can be imported."""
    logging.debug("Testing RateLimitMiddleware import")
    try:
        from swarmauri_middleware_ratelimit import RateLimitMiddleware

        assert isinstance(RateLimitMiddleware, type), (
            "RateLimitMiddleware should be a class"
        )
    except ImportError:
        pytest.skip("RateLimitMiddleware not found, possibly not installed")


def test_init_module_contents():
    """Test the contents of the __init__ module."""
    mod = import_module("swarmauri_middleware_ratelimit")
    assert hasattr(mod, "RateLimitMiddleware"), (
        "RateLimitMiddleware should be in __init__"
    )
    assert "RateLimitMiddleware" in mod.__all__, (
        "RateLimitMiddleware should be in __all__"
    )
