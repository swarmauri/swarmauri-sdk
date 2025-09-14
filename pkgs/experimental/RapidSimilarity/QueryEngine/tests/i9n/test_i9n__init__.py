import pytest


@pytest.fixture(scope="module")
def setup_module() -> None:
    """Fixture to set up the test module."""
    # Perform any necessary setup here, if needed
    pass


@pytest.mark.i9n
def test_import_cpp_extension(setup_module) -> None:
    """Test that the C++ extension can be imported successfully."""
    try:
        # Attempt to import a specific C++ extension from QueryEngine
        import QueryEngine.cpp_extension as cpp_extension  # Change to your actual C++ extension name

        assert cpp_extension is not None
    except ImportError as e:
        pytest.fail(f"Failed to import C++ extension: {e}")


@pytest.mark.i9n
def test_query_functionality(setup_module) -> None:
    """Test that a C++ function can be called from Python."""
    try:
        from QueryEngine.cpp_extension import (
            example_function,
        )  # Change to your actual function

        result = example_function(42)  # Example input; adjust as necessary
        assert result is not None  # Replace with your expected value
    except ImportError as e:
        pytest.fail(f"Failed to import function from C++ extension: {e}")
    except Exception as e:
        pytest.fail(f"Function call failed: {e}")
