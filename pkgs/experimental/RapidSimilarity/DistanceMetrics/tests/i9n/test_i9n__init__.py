import pytest


@pytest.mark.i9n
def test_import_cpp_extension() -> None:
    """Verify that the DistanceMetrics extension can be imported."""
    try:
        import DistanceMetrics.extensions as extensions

        assert extensions is not None
    except ImportError as e:
        pytest.fail(f"Failed to import C++ extension: {e}")


@pytest.mark.i9n
def test_functionality_of_cpp_extension() -> None:
    """Test that a specific function from the C++ extension works correctly."""
    import DistanceMetrics.extensions

    result = DistanceMetrics.extensions.example_function()
    assert result is not None, "C++ extension function returned None."


@pytest.mark.i9n
def test_numpy_integration() -> None:
    """Test the integration of NumPy with the C++ extension."""
    import numpy as np
    import DistanceMetrics.extensions

    array = np.array([1.0, 2.0, 3.0])
    result = DistanceMetrics.extensions.numpy_function(array)
    assert isinstance(result, np.ndarray), (
        "The result should be a NumPy array."
    )
    assert result.shape == array.shape, (
        "The shape of the result should match the input array."
    )
