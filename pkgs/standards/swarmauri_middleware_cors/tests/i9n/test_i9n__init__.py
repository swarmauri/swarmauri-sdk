"""
Tests for the __init__.py module in the swarmauri_middleware_cors package.
"""

import pytest
import logging
from swarmauri_middleware_cors import __init__ as init_module

LOGGER = logging.getLogger(__name__)


@pytest.mark.i9n
class TestInit:
    """
    Test cases for the __init__.py module.
    
    Ensures that the package initializer loads correctly and exports the expected components.
    """
    
    def test_custom_cors_middleware_import(self):
        """
        Tests that CustomCORSMiddleware can be imported and instantiated.
        
        Verifies that the CustomCORSMiddleware class is correctly exported
        in the __init__.py file.
        """
        LOGGER.debug("Testing CustomCORSMiddleware import")
        from swarmauri_middleware_cors import CustomCORSMiddleware
        
        # Test instantiation
        cors_middleware = CustomCORSMiddleware(
            allow_origins=["*"],
            allow_credentials=True,
            expose_headers=["*"],
            max_age=3600,
        )
        
        assert cors_middleware is not None
        LOGGER.debug("CustomCORSMiddleware imported successfully")
        
    def test_version_defined(self):
        """
        Tests that the __version__ variable is defined and accessible.
        
        Verifies that the version is properly set and can be retrieved
        from the __init__.py module.
        """
        LOGGER.debug("Testing __version__ definition")
        assert isinstance(init_module.__version__, str)
        assert init_module.__version__ != ""
        LOGGER.debug(f"Package version: {init_module.__version__}")
        
    def test_all_definition(self):
        """
        Tests that the __all__ variable is defined and contains expected values.
        
        Verifies that the __all__ list includes the necessary components
        for proper exporting.
        """
        LOGGER.debug("Testing __all__ definition")
        assert isinstance(init_module.__all__, list)
        assert "CustomCORSMiddleware" in init_module.__all__
        LOGGER.debug(f"__all__ contents: {init_module.__all__}")