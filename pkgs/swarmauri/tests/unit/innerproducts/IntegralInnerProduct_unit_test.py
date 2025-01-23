import pytest
from swarmauri.innerproducts.concrete.L2InnerProduct import L2InnerProduct
import math

@pytest.mark.unit
def test_ubc_type():
    """
    Test the type attribute of L2InnerProduct.
    """
    integral_inner_product = L2InnerProduct()
    assert integral_inner_product.type == 'L2InnerProduct'


@pytest.mark.unit
def test_resource_type():
    """
    Test the resource attribute of L2InnerProduct.
    """
    integral_inner_product = L2InnerProduct()
    assert integral_inner_product.resource == 'InnerProduct'


@pytest.mark.unit
def test_serialization():
    """
    Test serialization and deserialization of L2InnerProduct.
    """
    integral_inner_product = L2InnerProduct()
    serialized = integral_inner_product.model_dump_json()
    deserialized = L2InnerProduct.model_validate_json(serialized)

    assert integral_inner_product.id == deserialized.id


@pytest.mark.unit
def test_integral_inner_product_computation():
    """
    Test the computation of the integral inner product.
    """
    f = lambda x: x
    g = lambda x: x**2
    a, b = 0, 1
    integral_inner_product = L2InnerProduct()

    # Manual computation: ∫_0^1 x * x^2 dx = ∫_0^1 x^3 dx = [x^4 / 4]_0^1 = 1/4
    assert pytest.approx(integral_inner_product.compute(f, g, a, b), 0.0001) == 0.25


@pytest.mark.unit
def test_invalid_interval():
    """
    Test that a ValueError is raised for an invalid interval.
    """
    f = lambda x: x
    g = lambda x: x
    a, b = 1, 0
    integral_inner_product = L2InnerProduct()

    with pytest.raises(ValueError):
        integral_inner_product.compute(f, g, a, b)


@pytest.mark.unit
def test_check_conjugate_symmetry():
    """
    Test the conjugate symmetry property of the integral inner product.
    """
    f = lambda x: x
    g = lambda x: x**2
    a, b = 0, 1
    integral_inner_product = L2InnerProduct()

    assert integral_inner_product.check_conjugate_symmetry(f, g)


@pytest.mark.unit
def test_check_linearity_first_argument():
    """
    Test the linearity in the first argument property of the integral inner product.
    """
    f = lambda x: x
    g = lambda x: x**2
    h = lambda x: 1
    alpha = 2
    a, b = 0, 1
    integral_inner_product = L2InnerProduct()

    assert integral_inner_product.check_linearity_first_argument(f, g, h, alpha)


@pytest.mark.unit
def test_check_positivity():
    """
    Test the positivity property of the integral inner product.
    """
    f = lambda x: x
    g = lambda x: lambda x: 0  # Zero function
    a, b = 0, 1
    integral_inner_product = L2InnerProduct()

    assert integral_inner_product.check_positivity(f)
    assert not integral_inner_product.check_positivity(g)


@pytest.mark.unit
def test_check_all_axioms():
    """
    Test all the axioms for the integral inner product.
    """
    f = lambda x: x
    g = lambda x: x**2
    h = lambda x: 1
    alpha = 2
    a, b = 0, 1
    integral_inner_product = L2InnerProduct()

    assert integral_inner_product.check_all_axioms(f, g, h, alpha)

@pytest.mark.unit
def test_check_cauchy_schwarz_inequality():
    """
    Test the Cauchy-Schwarz inequality for the integral inner product.
    """
    f = lambda x: x
    g = lambda x: x**2
    a, b = 0, 1
    integral_inner_product = L2InnerProduct()

    # Check if the inequality holds
    assert integral_inner_product.check_cauchy_schwarz_inequality(f, g, a, b)

    # Test with the zero function
    zero_function = lambda x: 0
    assert integral_inner_product.check_cauchy_schwarz_inequality(f, zero_function, a, b)

    # Test with the same function (Cauchy-Schwarz becomes equality)
    identical_function = lambda x: x
    assert integral_inner_product.check_cauchy_schwarz_inequality(identical_function, identical_function, a, b)

    # Test with orthogonal-like functions over the interval
    # f(x) = x and g(x) = 1-x are orthogonal on [0, 1], since ∫_0^1 x * (1 - x) dx = 0
    orthogonal_f = lambda x: x
    orthogonal_g = lambda x: 1 - x
    assert integral_inner_product.check_cauchy_schwarz_inequality(orthogonal_f, orthogonal_g, a, b)
