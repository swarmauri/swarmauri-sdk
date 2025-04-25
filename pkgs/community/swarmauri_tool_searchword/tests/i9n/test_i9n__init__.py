import pytest
import logging
from swarmauri_tool_searchword import __init__ as swarmauri_init

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.mark.i9n
def test_init_loads_correctly() -> None:
    """Test that the swarmauri_tool_searchword package __init__.py loads correctly."""
    try:
        # Attempt to access the package version and ensure it is defined
        assert hasattr(swarmauri_init, '__version__'), "Version attribute is missing from __init__"
        logger.info("Version attribute is present: %s", swarmauri_init.__version__)

        # Ensure that the expected modules are accessible
        expected_modules = ['SearchWordTool']
        for module in expected_modules:
            assert module in swarmauri_init.__all__, f"{module} is not in __all__"
            logger.info("%s is correctly defined in __all__", module)
            
    except Exception as e:
        logger.error("Error while testing __init__: %s", str(e))
        raise e  # Re-raise the exception for pytest to catch it

@pytest.fixture(scope='module')
def setup_package() -> None:
    """Fixture to set up the swarmauri_tool_searchword package."""
    # Here we can include any setup logic needed before tests run
    logger.info("Setting up the swarmauri_tool_searchword package for tests.")
    yield  # This allows the test to run
    # Any teardown logic can be added here if needed
    logger.info("Teardown after tests completed.")