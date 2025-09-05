import importlib
import logging
from logging import Logger

import pytest

# Set up logging
logging.basicConfig(level=logging.DEBUG)
LOGGER: Logger = logging.getLogger(__name__)


@pytest.mark.i9n
class TestInit:
    """Test class for __init__.py module verification."""

    @pytest.fixture(scope="class")
    def init_module(self):
        """Fixture that imports the init module."""
        return importlib.import_module("swarmauri_middleware_cors")

    def test_custom_cors_middleware_import(self, init_module):
        """Test that CustomCORSMiddleware can be imported."""
        LOGGER.debug("Testing CustomCORSMiddleware import")
        assert hasattr(init_module, "CustomCORSMiddleware")
        assert isinstance(init_module.CustomCORSMiddleware, type)

    def test_version_defined(self, init_module):
        """Tests that the __version__ variable is defined and accessible."""
        LOGGER.debug("Testing __version__ definition")
        assert hasattr(init_module, "__version__")
        assert isinstance(init_module.__version__, str)

    def test_all_definition(self, init_module):
        """Tests that the __all__ variable is defined and contains expected values."""
        LOGGER.debug("Testing __all__ definition")
        assert hasattr(init_module, "__all__")
        assert isinstance(init_module.__all__, list)
        assert "CustomCORSMiddleware" in init_module.__all__
