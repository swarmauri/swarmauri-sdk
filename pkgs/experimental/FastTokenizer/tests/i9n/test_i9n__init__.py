import pytest
import logging
from fasttokenizer import __init__

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@pytest.mark.i9n
def test_i9n_init():
    # Test that the Rust extension loads correctly
    try:
        __init__.rust_init()
        logger.debug("Rust extension loaded successfully")
        assert True
    except Exception as e:
        logger.error(f"Error loading Rust extension: {str(e)}")
        assert False

@pytest.mark.i9n
def test_i9n_teardown():
    # Test that the Rust extension unloads correctly
    try:
        __init__.rust_teardown()
        logger.debug("Rust extension unloaded successfully")
        assert True
    except Exception as e:
        logger.error(f"Error unloading Rust extension: {str(e)}")
        assert False

@pytest.mark.i9n
def test_i9n_version():
    # Test that the version number is correctly retrieved
    version = __init__.get_version()
    assert isinstance(version, str) and version!= ""