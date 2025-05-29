import pytest
import logging
from importlib import import_module
from swarmauri_middleware_logging import __version__, LoggingMiddleware

@pytest.mark.i9n
class TestInit:
    """Tests for the package initializer."""

    def test_version(self):
        """Test that the package version is correctly set."""
        assert isinstance(__version__, str)
        logging.info("Test version: %s", __version__)

    def test_logging_middleware_import(self):
        """Test that LoggingMiddleware is properly imported."""
        assert LoggingMiddleware is not None
        logging.info("LoggingMiddleware imported: %s",
                    LoggingMiddleware)

    def test_all_reference(self):
        """Test that LoggingMiddleware is in __all__."""
        init_module = import_module("swarmauri_middleware_logging")
        assert LoggingMiddleware in init_module.__all__
        logging.info("__all__ contents: %s", init_module.__all__)

    def test_version_fallback(self):
        """Test that the version fallback works when package is not installed."""
        try:
            # Simulate PackageNotFoundError by overriding __version__
            original_version = __version__
            __version__ = None
            from swarmauri_middleware_logging import __version__ as test_version
            assert test_version == "0.0.0"
        except Exception as e:
            logging.error("Version fallback test failed: %s", str(e))
            pytest.fail(str(e))
        finally:
            __version__ = original_version
        logging.info("Version fallback test passed")