import pytest
import importlib
import logging
from logging import Logger

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger: Logger = logging.getLogger(__name__)


@pytest.mark.i9n
def test_init_module() -> None:
    """
    Tests that the __init__.py module loads correctly and exports the expected components.

    This test verifies that the module can be imported and that the expected
    classes and variables are available in the module's namespace.
    """
    logger.debug("Starting test_init_module")

    # Dynamically import the __init__ module
    module = importlib.import_module("swarmauri_middleware_bulkhead")

    # Verify that the __version__ string is correctly set
    assert hasattr(module, "__version__")
    assert isinstance(module.__version__, str)
    logger.debug("Verified __version__ string")

    # Verify that BulkheadMiddleware is correctly imported
    assert hasattr(module, "BulkheadMiddleware")
    assert isinstance(module.BulkheadMiddleware, type)
    logger.debug("Verified BulkheadMiddleware import")

    logger.debug("Completed test_init_module successfully")
