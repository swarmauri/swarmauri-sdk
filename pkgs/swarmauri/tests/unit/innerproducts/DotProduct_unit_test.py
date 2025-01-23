import pytest
from swarmauri.vectors.concrete.Vector import Vector
from swarmauri.innerproducts.concrete.DotProduct import DotProduct

@pytest.mark.unit
def test_ubc_type():
    """
    Test that the type attribute of DotProduct is correctly set.
    """
    dot_product = DotProduct()
    assert dot_product.type == 'DotProduct'


@pytest.mark.unit
def test_resource_type():
    """
    Test that the resource attribute of DotProduct is correctly set.
    """
    dot_product = DotProduct()
    assert dot_product.resource == 'InnerProduct'


@pytest.mark.unit
def test_serialization():
    """
    Test that the DotProduct instance can be serialized and deserialized correctly.
    """
    dot_product = DotProduct()
    serialized = dot_product.model_dump_json()
    deserialized = DotProduct.model_validate_json(serialized)

    assert dot_product.id == deserialized.id


@pytest.mark.unit
def test_compute():
    """
    Test the computation of the dot product of two vectors.
    """
    u = Vector(value=[1, 2, 3])
    v = Vector(value=[4, 5, 6])
    dot_product = DotProduct()

    expected_result = 1 * 4 + 2 * 5 + 3 * 6
    assert dot_product.compute(u, v) == expected_result


@pytest.mark.unit
def test_zero():
    """
    Test the dot product when one of the vectors is a zero vector.
    """
    u = Vector(value=[0, 0, 0])
    v = Vector(value=[1, 2, 3])
    dot_product = DotProduct()

    assert dot_product.compute(u, v) == 0.0


@pytest.mark.unit
def test_orthogonal():
    """
    Test the dot product of two orthogonal vectors.
    """
    u = Vector(value=[1, 0])
    v = Vector(value=[0, 1])
    dot_product = DotProduct()

    assert dot_product.compute(u, v) == 0.0


@pytest.mark.unit
def test_negative():
    """
    Test the dot product of vectors with negative components.
    """
    u = Vector(value=[1, -2, 3])
    v = Vector(value=[-4, 5, -6])
    dot_product = DotProduct()

    expected_result = (1 * -4) + (-2 * 5) + (3 * -6)
    assert dot_product.compute(u, v) == expected_result


@pytest.mark.unit
def test_dimension_mismatch():
    """
    Test that a ValueError is raised when vectors of different dimensions are provided.
    """
    u = Vector(value=[1, 2])
    v = Vector(value=[4, 5, 6])
    dot_product = DotProduct()

    with pytest.raises(ValueError):
        dot_product.compute(u, v)


@pytest.mark.unit
def test_check_conjugate_symmetry():
    """
    Test the conjugate symmetry property of the dot product.
    """
    u = Vector(value=[1, 2])
    v = Vector(value=[3, 4])
    dot_product = DotProduct()

    assert dot_product.check_conjugate_symmetry(u, v)


@pytest.mark.unit
def test_check_linearity_first_argument():
    """
    Test the linearity in the first argument property of the dot product.
    """
    u = Vector(value=[1, 0])
    v = Vector(value=[0, 1])
    w = Vector(value=[1, 1])
    alpha = 2
    dot_product = DotProduct()

    # Manually compute αu + v
    scaled_u_values = [alpha * u_i for u_i in u.value]
    scaled_sum_values = [scaled_u_values[i] + v.value[i] for i in range(len(u.value))]
    combined_vector = Vector(value=scaled_sum_values)

    result_left = dot_product.compute(combined_vector, w)
    result_right = alpha * dot_product.compute(u, w) + dot_product.compute(v, w)

    assert pytest.approx(result_left) == pytest.approx(result_right)


@pytest.mark.unit
def test_check_positivity():
    """
    Test the positivity property of the dot product.
    """
    u = Vector(value=[1, 2, 3])
    v = Vector(value=[0, 0, 0])  # Zero vector
    dot_product = DotProduct()

    assert dot_product.check_positivity(u)
    assert not dot_product.check_positivity(v)


@pytest.mark.unit
def test_check_all_axioms():
    """
    Test all the axioms for the dot product.
    """
    u = Vector(value=[1, 0])
    v = Vector(value=[0, 1])
    w = Vector(value=[1, 1])
    alpha = 2
    dot_product = DotProduct()

    assert dot_product.check_conjugate_symmetry(u, v)
    assert dot_product.check_linearity_first_argument(u, v, w, alpha)
    assert dot_product.check_positivity(u)

@pytest.mark.unit
def test_check_cauchy_schwarz_inequality():
    """
    Test the Cauchy-Schwarz inequality for the dot product.
    """
    u = Vector(value=[1, 2, 3])
    v = Vector(value=[4, 5, 6])
    dot_product = DotProduct()

    # Check if the inequality holds
    assert dot_product.check_cauchy_schwarz_inequality(u, v)

    # Test with a zero vector
    zero_vector = Vector(value=[0, 0, 0])
    assert dot_product.check_cauchy_schwarz_inequality(u, zero_vector)

    # Test with orthogonal vectors
    orthogonal_u = Vector(value=[1, 0])
    orthogonal_v = Vector(value=[0, 1])
    assert dot_product.check_cauchy_schwarz_inequality(orthogonal_u, orthogonal_v)

    # Test with identical vectors (Cauchy-Schwarz becomes equality)
    identical_u = Vector(value=[3, 4, 5])
    identical_v = Vector(value=[3, 4, 5])
    assert dot_product.check_cauchy_schwarz_inequality(identical_u, identical_v)

    # Test with negative components
    negative_u = Vector(value=[-1, -2, -3])
    negative_v = Vector(value=[-4, -5, -6])
    assert dot_product.check_cauchy_schwarz_inequality(negative_u, negative_v)
