import pytest
import numpy as np
from swarmauri.innerproducts.concrete.FrobeniusInnerProduct import FrobeniusInnerProduct

@pytest.mark.unit
def test_ubc_type():
    """
    Test the type attribute of FrobeniusInnerProduct.
    """
    frobenius_inner_product = FrobeniusInnerProduct()
    assert frobenius_inner_product.type == 'FrobeniusInnerProduct'


@pytest.mark.unit
def test_resource_type():
    """
    Test the resource attribute of FrobeniusInnerProduct.
    """
    frobenius_inner_product = FrobeniusInnerProduct()
    assert frobenius_inner_product.resource == 'InnerProduct'


@pytest.mark.unit
def test_serialization():
    """
    Test serialization and deserialization of FrobeniusInnerProduct.
    """
    frobenius_inner_product = FrobeniusInnerProduct()
    serialized = frobenius_inner_product.model_dump_json()
    deserialized = FrobeniusInnerProduct.model_validate_json(serialized)

    assert frobenius_inner_product.id == deserialized.id


@pytest.mark.unit
def test_frobenius_inner_product_computation():
    """
    Test the computation of the Frobenius inner product.
    """
    A = np.array([[1, 2], [3, 4]])
    B = np.array([[5, 6], [7, 8]])
    frobenius_inner_product = FrobeniusInnerProduct()

    assert frobenius_inner_product.compute(A, B) == 70  # Manual calculation: 1*5 + 2*6 + 3*7 + 4*8


@pytest.mark.unit
def test_frobenius_inner_product_dimension_mismatch():
    """
    Test that a ValueError is raised for matrices of different dimensions.
    """
    A = np.array([[1, 2], [3, 4]])
    B = np.array([[5, 6, 7], [8, 9, 10]])
    frobenius_inner_product = FrobeniusInnerProduct()

    with pytest.raises(ValueError):
        frobenius_inner_product.compute(A, B)


@pytest.mark.unit
def test_check_conjugate_symmetry():
    """
    Test the conjugate symmetry property of the Frobenius inner product.
    """
    A = np.array([[1, 2], [3, 4]])
    B = np.array([[5, 6], [7, 8]])
    frobenius_inner_product = FrobeniusInnerProduct()

    assert frobenius_inner_product.check_conjugate_symmetry(A, B)


@pytest.mark.unit
def test_check_linearity_first_argument():
    """
    Test the linearity in the first argument property of the Frobenius inner product.
    """
    A = np.array([[1, 0], [0, 1]])
    B = np.array([[0, 1], [1, 0]])
    C = np.array([[1, 1], [1, 1]])
    alpha = 2
    frobenius_inner_product = FrobeniusInnerProduct()

    assert frobenius_inner_product.check_linearity_first_argument(A, B, C, alpha)


@pytest.mark.unit
def test_check_positivity():
    """
    Test the positivity property of the Frobenius inner product.
    """
    A = np.array([[1, 2], [3, 4]])
    Z = np.array([[0, 0], [0, 0]])  # Zero matrix
    frobenius_inner_product = FrobeniusInnerProduct()

    assert frobenius_inner_product.check_positivity(A)
    assert not frobenius_inner_product.check_positivity(Z)


@pytest.mark.unit
def test_check_all_axioms():
    """
    Test all the axioms for the Frobenius inner product.
    """
    A = np.array([[1, 0], [0, 1]])
    B = np.array([[0, 1], [1, 0]])
    C = np.array([[1, 1], [1, 1]])
    alpha = 2
    frobenius_inner_product = FrobeniusInnerProduct()

    assert frobenius_inner_product.check_all_axioms(A, B, C, alpha)
    
@pytest.mark.unit
def test_check_cauchy_schwarz_inequality():
    """
    Test the Cauchy-Schwarz inequality for the Frobenius inner product.
    """
    A = np.array([[1, 2], [3, 4]])
    B = np.array([[5, 6], [7, 8]])
    frobenius_inner_product = FrobeniusInnerProduct()

    # Check if the inequality holds
    assert frobenius_inner_product.check_cauchy_schwarz_inequality(A, B)

    # Test with the zero matrix
    zero_matrix = np.array([[0, 0], [0, 0]])
    assert frobenius_inner_product.check_cauchy_schwarz_inequality(A, zero_matrix)

    # Test with identical matrices (Cauchy-Schwarz becomes equality)
    identical_matrix = np.array([[1, 2], [3, 4]])
    assert frobenius_inner_product.check_cauchy_schwarz_inequality(identical_matrix, identical_matrix)

    # Test with orthogonal-like matrices
    # A = [[1, 0], [0, 1]] and B = [[0, 1], [1, 0]] are "orthogonal" under Frobenius
    orthogonal_A = np.array([[1, 0], [0, 1]])
    orthogonal_B = np.array([[0, 1], [1, 0]])
    assert frobenius_inner_product.check_cauchy_schwarz_inequality(orthogonal_A, orthogonal_B)
