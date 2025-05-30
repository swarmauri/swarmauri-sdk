import logging
from importlib import import_module

import pytest

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.mark.i9n
class TestInit:
    """Tests for the package initializer."""

    def test_version(self):
        """Test that the version is correctly defined."""
        init_module = import_module("swarmauri_middleware_session")
        assert hasattr(init_module, "__version__"), "Package version is not defined"
        assert isinstance(init_module.__version__, str), (
            "Package version is not a string"
        )
        assert len(init_module.__version__) > 0, "Package version string is empty"
        logger.debug("Package version: %s", init_module.__version__)

    def test_all_definition(self):
        """Test that __all__ is correctly defined."""
        init_module = import_module("swarmauri_middleware_session")
        assert hasattr(init_module, "__all__"), "__all__ is not defined"
        assert isinstance(init_module.__all__, list), "__all__ is not a list"
        assert len(init_module.__all__) > 0, "__all__ is empty"
        logger.debug("__all__ contents: %s", init_module.__all__)

    @pytest.mark.i9n
    def test_session_middleware_import(self):
        """Test that SessionMiddleware is properly imported."""
        init_module = import_module("swarmauri_middleware_session")
        assert hasattr(init_module, "SessionMiddleware"), (
            "SessionMiddleware is not in __all__"
        )
        logger.debug("SessionMiddleware found in __all__")
