import logging
from importlib import import_module

import pytest


@pytest.mark.i9n
def test_module_loading() -> None:
    """
    Test that the module loads correctly.
    """
    logging.info("Testing module loading")
    module = import_module("swarmauri_middleware_securityheaders")
    assert module is not None, "Failed to import module"


@pytest.mark.i9n
def test_version() -> None:
    """
    Test that the version is correctly set.
    """
    logging.info("Testing version")
    module = import_module("swarmauri_middleware_securityheaders")
    assert hasattr(module, "__version__"), "Version not found"
    assert isinstance(module.__version__, str), "Version is not a string"
    # Check if version follows semantic versioning pattern
    import re

    version_pattern = r"^\d+\.\d+\.\d+$"
    # Fix: Use __version__ instead of __version_
    assert re.match(version_pattern, module.__version__), (
        "Version does not match expected pattern"
    )


@pytest.mark.i9n
def test_security_headers_middleware() -> None:
    """
    Test that SecurityHeadersMiddleware is properly exposed.
    """
    logging.info("Testing SecurityHeadersMiddleware")
    module = import_module("swarmauri_middleware_securityheaders")
    assert hasattr(module, "SecurityHeadersMiddleware"), (
        "SecurityHeadersMiddleware not found"
    )
    # Verify it's a class
    assert isinstance(module.SecurityHeadersMiddleware, type), (
        "SecurityHeadersMiddleware is not a class"
    )
    # Fix: Provide the required app parameter
    try:
        # Create a mock app function
        async def mock_app(request, call_next):
            return await call_next(request)

        instance = module.SecurityHeadersMiddleware(app=mock_app)
        assert instance is not None, "Failed to instantiate SecurityHeadersMiddleware"
    except Exception as e:
        pytest.fail(f"Failed to create SecurityHeadersMiddleware instance: {str(e)}")
