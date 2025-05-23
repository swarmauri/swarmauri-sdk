import importlib
import logging
import sys

import pytest

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@pytest.mark.i9n
def test_import_package():
    """
    Test that the swarmauri_evaluator_subprocess package can be imported.

    This test ensures that the package initializer loads correctly without any
    import errors.
    """
    try:
        # Attempt to import the package
        import swarmauri_evaluator_subprocess as package

        logger.info(
            f"Successfully imported swarmauri_evaluator_subprocess package - {package.__version__}"
        )
        assert True
    except ImportError as e:
        logger.error(f"Failed to import swarmauri_evaluator_subprocess: {e}")
        assert False, f"Failed to import swarmauri_evaluator_subprocess: {e}"


@pytest.mark.i9n
def test_version_attribute():
    """
    Test that the package has a __version__ attribute.

    This test verifies that the __version__ attribute is properly defined in the
    package's __init__.py file.
    """
    import swarmauri_evaluator_subprocess

    # Check if __version__ attribute exists
    assert hasattr(swarmauri_evaluator_subprocess, "__version__"), (
        "Package missing __version__ attribute"
    )

    # Check that version is a string
    assert isinstance(swarmauri_evaluator_subprocess.__version__, str), (
        "Package __version__ is not a string"
    )

    logger.info(f"Package version: {swarmauri_evaluator_subprocess.__version__}")


@pytest.mark.i9n
def test_subprocess_evaluator_import():
    """
    Test that SubprocessEvaluator can be imported from the package.

    This test ensures that the SubprocessEvaluator class is properly exposed
    in the package's public API.
    """
    try:
        # Test direct import from package
        from swarmauri_evaluator_subprocess import SubprocessEvaluator as evaluator

        logger.info(
            f"Successfully imported SubprocessEvaluator from package - {evaluator}"
        )
        assert True
    except ImportError as e:
        logger.error(f"Failed to import SubprocessEvaluator: {e}")
        assert False, f"Failed to import SubprocessEvaluator: {e}"


@pytest.mark.i9n
def test_all_attribute():
    """
    Test that the package has an __all__ attribute with expected contents.

    This test verifies that the __all__ list contains the expected exported classes.
    """
    import swarmauri_evaluator_subprocess

    # Check if __all__ attribute exists
    assert hasattr(swarmauri_evaluator_subprocess, "__all__"), (
        "Package missing __all__ attribute"
    )

    # Check that __all__ is a list or tuple
    assert isinstance(swarmauri_evaluator_subprocess.__all__, (list, tuple)), (
        "__all__ is not a list or tuple"
    )

    # Check that SubprocessEvaluator is in __all__
    assert "SubprocessEvaluator" in swarmauri_evaluator_subprocess.__all__, (
        "SubprocessEvaluator not in __all__"
    )

    logger.info(f"Package __all__: {swarmauri_evaluator_subprocess.__all__}")


@pytest.fixture
def reload_package():
    """
    Fixture to reload the package for testing.

    This ensures a clean import of the package for each test that uses this fixture.
    """
    if "swarmauri_evaluator_subprocess" in sys.modules:
        importlib.reload(sys.modules["swarmauri_evaluator_subprocess"])
    return importlib.import_module("swarmauri_evaluator_subprocess")


@pytest.mark.i9n
def test_package_reload(reload_package):
    """
    Test that the package can be reloaded without errors.

    This test ensures that the package can be reloaded dynamically, which is
    important for certain use cases like plugin systems or hot reloading.

    Args:
        reload_package: The pytest fixture that reloads the package
    """
    # The fixture already reloaded the package, so we just need to check it worked
    assert hasattr(reload_package, "SubprocessEvaluator"), (
        "Reloaded package missing SubprocessEvaluator"
    )
    logger.info("Successfully reloaded package")
