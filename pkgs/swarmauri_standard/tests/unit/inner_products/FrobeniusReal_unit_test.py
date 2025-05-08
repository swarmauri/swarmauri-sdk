import pytest
import numpy as np
import logging
from typing import List, Tuple, Any
from swarmauri_standard.inner_products.FrobeniusReal import FrobeniusReal


# Configure logging for testing
logging.basicConfig(level=logging.INFO)


@pytest.fixture
def frobenius_real() -> FrobeniusReal:
    """
    Fixture providing an instance of FrobeniusReal.
    
    Returns
    -------
    FrobeniusReal
        An instance of the FrobeniusReal inner product
    """
    return FrobeniusReal()


@pytest.mark.unit
def test_type():
    """Test that the type attribute is correctly set."""
    assert FrobeniusReal.type == "FrobeniusReal"


@pytest.mark.unit
def test_initialization():
    """Test that the FrobeniusReal class initializes correctly."""
    inner_product = FrobeniusReal()
    assert isinstance(inner_product, FrobeniusReal)
    assert inner_product.type == "FrobeniusReal"


@pytest.mark.unit
@pytest.mark.parametrize(
    "mat1, mat2, expected",
    [
        # Simple 2x2 matrices
        (
            [[1, 2], [3, 4]],
            [[5, 6], [7, 8]],
            1*5 + 2*6 + 3*7 + 4*8
        ),
        # Identity matrices
        (
            [[1, 0], [0, 1]],
            [[1, 0], [0, 1]],
            2
        ),
        # Zero and non-zero matrix
        (
            [[0, 0], [0, 0]],
            [[1, 2], [3, 4]],
            0
        ),
        # 1D arrays
        (
            [1, 2, 3],
            [4, 5, 6],
            1*4 + 2*5 + 3*6
        ),
        # Negative values
        (
            [[-1, -2], [-3, -4]],
            [[5, 6], [7, 8]],
            -1*5 + -2*6 + -3*7 + -4*8
        ),
        # Numpy arrays
        (
            np.array([[1.5, 2.5], [3.5, 4.5]]),
            np.array([[5.5, 6.5], [7.5, 8.5]]),
            1.5*5.5 + 2.5*6.5 + 3.5*7.5 + 4.5*8.5
        ),
    ]
)
def test_compute(
    frobenius_real: FrobeniusReal, 
    mat1: Any, 
    mat2: Any, 
    expected: float
):
    """
    Test the compute method with various matrix inputs.
    
    Parameters
    ----------
    frobenius_real : FrobeniusReal
        The FrobeniusReal instance from the fixture
    mat1 : Any
        First matrix for inner product
    mat2 : Any
        Second matrix for inner product
    expected : float
        Expected result of the inner product
    """
    result = frobenius_real.compute(mat1, mat2)
    assert np.isclose(result, expected)


@pytest.mark.unit
@pytest.mark.parametrize(
    "mat1, mat2, compatible",
    [
        # Same shape matrices
        (
            [[1, 2], [3, 4]],
            [[5, 6], [7, 8]],
            True
        ),
        # Different shape matrices
        (
            [[1, 2], [3, 4]],
            [[5, 6], [7, 8], [9, 10]],
            False
        ),
        # 1D arrays of same length
        (
            [1, 2, 3],
            [4, 5, 6],
            True
        ),
        # 1D arrays of different length
        (
            [1, 2, 3],
            [4, 5],
            False
        ),
        # Matrix and 1D array
        (
            [[1, 2], [3, 4]],
            [5, 6],
            False
        ),
        # Non-array inputs that can be converted
        (
            [1, 2, 3],
            (4, 5, 6),
            True
        ),
        # Empty arrays
        (
            [],
            [],
            True
        ),
    ]
)
def test_is_compatible(
    frobenius_real: FrobeniusReal, 
    mat1: Any, 
    mat2: Any, 
    compatible: bool
):
    """
    Test the is_compatible method with various inputs.
    
    Parameters
    ----------
    frobenius_real : FrobeniusReal
        The FrobeniusReal instance from the fixture
    mat1 : Any
        First matrix to check compatibility
    mat2 : Any
        Second matrix to check compatibility
    compatible : bool
        Expected compatibility result
    """
    result = frobenius_real.is_compatible(mat1, mat2)
    assert result == compatible


@pytest.mark.unit
def test_compute_raises_value_error_for_incompatible_matrices(frobenius_real: FrobeniusReal):
    """
    Test that compute raises ValueError for incompatible matrices.
    
    Parameters
    ----------
    frobenius_real : FrobeniusReal
        The FrobeniusReal instance from the fixture
    """
    mat1 = [[1, 2], [3, 4]]
    mat2 = [[1, 2, 3], [4, 5, 6]]
    
    with pytest.raises(ValueError):
        frobenius_real.compute(mat1, mat2)


@pytest.mark.unit
def test_compute_raises_type_error_for_non_convertible_inputs(frobenius_real: FrobeniusReal):
    """
    Test that compute raises TypeError for inputs that cannot be converted to arrays.
    
    Parameters
    ----------
    frobenius_real : FrobeniusReal
        The FrobeniusReal instance from the fixture
    """
    # Create inputs that can't be converted to real-valued arrays
    mat1 = "not an array"
    mat2 = [[1, 2], [3, 4]]
    
    with pytest.raises(TypeError):
        frobenius_real.compute(mat1, mat2)


@pytest.mark.unit
def test_serialization():
    """Test that the class can be properly serialized and deserialized."""
    frobenius_real = FrobeniusReal()
    serialized = frobenius_real.model_dump_json()
    deserialized = FrobeniusReal.model_validate_json(serialized)
    
    assert isinstance(deserialized, FrobeniusReal)
    assert deserialized.type == "FrobeniusReal"


@pytest.mark.unit
def test_large_matrices(frobenius_real: FrobeniusReal):
    """
    Test the compute method with larger matrices.
    
    Parameters
    ----------
    frobenius_real : FrobeniusReal
        The FrobeniusReal instance from the fixture
    """
    # Create two 100x100 matrices
    size = 100
    mat1 = np.ones((size, size))
    mat2 = np.ones((size, size)) * 2
    
    # Expected result: sum of all products (1*2) = size*size*2
    expected = size * size * 2
    result = frobenius_real.compute(mat1, mat2)
    
    assert np.isclose(result, expected)