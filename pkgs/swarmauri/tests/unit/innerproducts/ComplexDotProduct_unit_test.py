import pytest
from swarmauri.vectors.concrete.Vector import Vector
from swarmauri.innerproducts.concrete.ComplexDotProduct import ComplexDotProduct

@pytest.mark.unit
def test_ubc_type():
    """
    Test that the type attribute of ComplexDotProduct is correctly set.
    """
    complex_dot_product = ComplexDotProduct()
    assert complex_dot_product.type == 'ComplexDotProduct'


@pytest.mark.unit
def test_resource_type():
    """
    Test that the resource attribute of ComplexDotProduct is correctly set.
    """
    complex_dot_product = ComplexDotProduct()
    assert complex_dot_product.resource == 'InnerProduct'


@pytest.mark.unit
def test_serialization():
    """
    Test that the ComplexDotProduct instance can be serialized and deserialized correctly.
    """
    complex_dot_product = ComplexDotProduct()
    serialized = complex_dot_product.model_dump_json()
    deserialized = ComplexDotProduct.model_validate_json(serialized)

    assert complex_dot_product.id == deserialized.id


@pytest.mark.unit
def test_compute():
    """
    Test the computation of the complex dot product of two vectors.
    """
    u = Vector(value=[1 + 2j, 3 + 4j])
    v = Vector(value=[5 + 6j, 7 + 8j])
    complex_dot_product = ComplexDotProduct()

    expected_result = (1 + 2j) * (5 - 6j) + (3 + 4j) * (7 - 8j)  # Conjugate v
    assert complex_dot_product.compute(u, v) == expected_result


@pytest.mark.unit
def test_zero():
    """
    Test the complex dot product when one of the vectors is a zero vector.
    """
    u = Vector(value=[0 + 0j, 0 + 0j])
    v = Vector(value=[1 + 2j, 3 + 4j])
    complex_dot_product = ComplexDotProduct()

    assert complex_dot_product.compute(u, v) == 0.0


@pytest.mark.unit
def test_orthogonal():
    """
    Test the complex dot product of two orthogonal vectors.
    """
    u = Vector(value=[1 + 1j, -1 - 1j])
    v = Vector(value=[1 - 1j, 1 - 1j])
    complex_dot_product = ComplexDotProduct()

    assert complex_dot_product.compute(u, v) == 0.0


@pytest.mark.unit
def test_negative():
    """
    Test the complex dot product of vectors with negative components.
    """
    u = Vector(value=[-1 - 2j, -3 - 4j])
    v = Vector(value=[-5 - 6j, -7 - 8j])
    complex_dot_product = ComplexDotProduct()

    expected_result = (-1 - 2j) * (-5 + 6j) + (-3 - 4j) * (-7 + 8j)
    assert complex_dot_product.compute(u, v) == expected_result

@pytest.mark.unit
def test_dimension_mismatch():
    """
    Test that a ValueError is raised when vectors of different dimensions are provided.
    """
    u = Vector(value=[1 + 2j, 3 + 4j])
    v = Vector(value=[5 + 6j])
    complex_dot_product = ComplexDotProduct()

    with pytest.raises(ValueError):
        complex_dot_product.compute(u, v)


@pytest.mark.unit
def test_check_conjugate_symmetry():
    """
    Test the conjugate symmetry property of the complex dot product.
    """
    u = Vector(value=[1 + 2j, 3 + 4j])
    v = Vector(value=[5 + 6j, 7 + 8j])
    complex_dot_product = ComplexDotProduct()

    result_uv = complex_dot_product.compute(u, v)
    result_vu = complex_dot_product.compute(v, u)

    assert pytest.approx(result_uv) == pytest.approx(result_vu.conjugate())


@pytest.mark.unit
def test_check_linearity_first_argument():
    """
    Test the linearity in the first argument property of the complex dot product.
    """
    u = Vector(value=[1 + 2j, 3 + 4j])
    v = Vector(value=[5 + 6j, 7 + 8j])
    w = Vector(value=[9 + 10j, 11 + 12j])
    alpha = 2 + 3j
    complex_dot_product = ComplexDotProduct()

    scaled_u_values = [alpha * x for x in u.value]
    combined_values = [scaled_u_values[i] + v.value[i] for i in range(len(u.value))]
    combined_vector = Vector(value=combined_values)

    result_left = complex_dot_product.compute(combined_vector, w)
    result_right = alpha * complex_dot_product.compute(u, w) + complex_dot_product.compute(v, w)

    assert pytest.approx(result_left) == pytest.approx(result_right)


@pytest.mark.unit
def test_check_positivity():
    """
    Test the positivity property of the complex dot product.
    """
    u = Vector(value=[1 + 2j, 3 + 4j])
    v = Vector(value=[0 + 0j, 0 + 0j])  # Zero vector
    complex_dot_product = ComplexDotProduct()

    assert complex_dot_product.check_positivity(u)
    assert not complex_dot_product.check_positivity(v)


@pytest.mark.unit
def test_check_all_axioms():
    """
    Test all the axioms for the complex dot product.
    """
    u = Vector(value=[1 + 1j, 2 + 2j])
    v = Vector(value=[3 + 3j, 4 + 4j])
    w = Vector(value=[5 + 5j, 6 + 6j])
    alpha = 2 + 3j
    complex_dot_product = ComplexDotProduct()

    assert complex_dot_product.check_conjugate_symmetry(u, v)
    assert complex_dot_product.check_linearity_first_argument(u, v, w, alpha)
    assert complex_dot_pr

@pytest.mark.unit
def test_check_cauchy_schwarz_inequality():
    """
    Test the Cauchy-Schwarz inequality for the complex dot product.
    """
    u = Vector(value=[1 + 2j, 3 + 4j])
    v = Vector(value=[5 + 6j, 7 + 8j])
    complex_dot_product = ComplexDotProduct()

    # Check if the inequality holds
    assert complex_dot_product.check_cauchy_schwarz_inequality(u, v)

    # Test with a zero vector
    zero_vector = Vector(value=[0 + 0j, 0 + 0j])
    assert complex_dot_product.check_cauchy_schwarz_inequality(u, zero_vector)

    # Test with orthogonal vectors (Cauchy-Schwarz becomes equality when orthogonal)
    orthogonal_u = Vector(value=[1 + 1j, -1 - 1j])
    orthogonal_v = Vector(value=[1 - 1j, 1 - 1j])
    assert complex_dot_product.check_cauchy_schwarz_inequality(orthogonal_u, orthogonal_v)

    # Test with real-valued vectors
    real_u = Vector(value=[1, 2])
    real_v = Vector(value=[3, 4])
    assert complex_dot_product.check_cauchy_schwarz_inequality(real_u, real_v)