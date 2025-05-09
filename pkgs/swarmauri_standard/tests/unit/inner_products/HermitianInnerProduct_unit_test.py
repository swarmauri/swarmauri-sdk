import pytest
import numpy as np
from swarmauri_standard.swarmauri_standard.inner_products.HermitianInnerProduct import (
    HermitianInnerProduct,
)
from swarmauri_standard.swarmauri_standard.inner_products.IInnerProduct import (
    IInnerProduct,
)


@pytest.mark.unit
def test_hermitian_inner_product_resource() -> None:
    """Test that the resource attribute is correctly set."""
    assert HermitianInnerProduct.resource == "Inner_product"


@pytest.mark.unit
def test_hermitian_inner_product_type() -> None:
    """Test that the type attribute is correctly set."""
    assert HermitianInnerProduct.type == "HermitianInnerProduct"


@pytest.mark.unit
def test_compute() -> None:
    """Test the compute method of HermitianInnerProduct."""
    hip = HermitianInnerProduct()

    # Test with real vectors
    x = np.array([1, 2, 3])
    y = np.array([4, 5, 6])
    result = hip.compute(x, y)

    # Expected result using real vectors (dot product)
    expected = np.dot(x, y)
    assert result == expected

    # Test with complex vectors
    x_complex = np.array([1 + 1j, 2 + 2j, 3 + 3j])
    y_complex = np.array([4 + 4j, 5 + 5j, 6 + 6j])
    result_complex = hip.compute(x_complex, y_complex)

    # Expected result using complex vectors
    expected_complex = np.dot(x_complex.conj(), y_complex)
    assert np.isclose(result_complex, expected_complex)


@pytest.mark.unit
def test_check_conjugate_symmetry() -> None:
    """Test conjugate symmetry property."""
    hip = HermitianInnerProduct()

    # Create complex vectors
    x = np.array([1 + 1j, 2 + 2j])
    y = np.array([3 + 3j, 4 + 4j])

    # Compute inner products
    inner_xy = hip.compute(x, y)
    inner_yx = hip.compute(y, x)

    # Check conjugate symmetry
    assert np.isclose(inner_xy, inner_yx.conjugate())


@pytest.mark.unit
def test_check_linearity_first_argument() -> None:
    """Test linearity in the first argument."""
    hip = HermitianInnerProduct()

    # Create vectors
    x = np.array([1, 2])
    y = np.array([3, 4])
    z = np.array([5, 6])

    a = 2.0
    b = 3.0

    # Compute left side: a<x,z> + b<y,z>
    left = a * hip.compute(x, z) + b * hip.compute(y, z)

    # Compute right side: <a x + b y, z>
    ax_by = a * x + b * y
    right = hip.compute(ax_by, z)

    # Check equality with tolerance
    assert np.isclose(left, right)


@pytest.mark.unit
def test_check_positivity() -> None:
    """Test positive definiteness."""
    hip = HermitianInnerProduct()

    # Create non-zero vector
    x = np.array([1 + 1j, 2 + 2j])
    result = hip.compute(x, x)

    # Result should be positive
    assert result > 0.0


@pytest.mark.unit
def test_serialization() -> None:
    """Test serialization and deserialization."""
    hip = HermitianInnerProduct()
    dumped = hip.model_dump_json()
    loaded_id = HermitianInnerProduct.model_validate_json(dumped)
    assert hip.id == loaded_id


@pytest.mark.unit
def test_compute_with_real_vectors() -> None:
    """Test compute method with real vectors."""
    hip = HermitianInnerProduct()

    x = np.array([1, 2, 3], dtype=np.float64)
    y = np.array([4, 5, 6], dtype=np.float64)

    result = hip.compute(x, y)
    expected = np.dot(x, y)
    assert result == expected


@pytest.mark.unit
def test_compute_with_complex_vectors() -> None:
    """Test compute method with complex vectors."""
    hip = HermitianInnerProduct()

    x = np.array([1 + 1j, 2 + 2j, 3 + 3j])
    y = np.array([4 + 4j, 5 + 5j, 6 + 6j])

    result = hip.compute(x, y)
    expected = np.dot(x.conj(), y)
    assert np.isclose(result, expected)


@pytest.mark.unit
def test_compute_raises_value_error_for_non_complex_vectors() -> None:
    """Test that compute raises ValueError for non-complex vectors."""
    hip = HermitianInnerProduct()

    x = np.array([1, 2, 3])
    y = np.array([4, 5, 6])

    with pytest.raises(ValueError):
        hip.compute(x, y)


@pytest.mark.unit
def test_check_conjugate_symmetry_with_complex_vectors() -> None:
    """Test conjugate symmetry with complex vectors."""
    hip = HermitianInnerProduct()

    x = np.array([1 + 1j, 2 + 2j])
    y = np.array([3 + 3j, 4 + 4j])

    inner_xy = hip.compute(x, y)
    inner_yx = hip.compute(y, x)

    assert np.isclose(inner_xy, inner_yx.conjugate())


@pytest.mark.unit
def test_check_linearity_with_complex_vectors() -> None:
    """Test linearity with complex vectors."""
    hip = HermitianInnerProduct()

    x = np.array([1 + 1j, 2 + 2j])
    y = np.array([3 + 3j, 4 + 4j])
    z = np.array([5 + 5j, 6 + 6j])

    a = 2.0
    b = 3.0

    left = a * hip.compute(x, z) + b * hip.compute(y, z)
    ax_by = a * x + b * y
    right = hip.compute(ax_by, z)

    assert np.isclose(left, right)


@pytest.mark.unit
def test_check_positivity_with_complex_vector() -> None:
    """Test positive definiteness with complex vector."""
    hip = HermitianInnerProduct()

    x = np.array([1 + 1j, 2 + 2j])
    result = hip.compute(x, x)

    assert result > 0.0


@pytest.mark.unit
def test_compute_with_zero_vector() -> None:
    """Test compute method with zero vector."""
    hip = HermitianInnerProduct()

    x = np.array([0.0, 0.0])
    y = np.array([0.0, 0.0])

    result = hip.compute(x, y)
    assert result == 0.0
