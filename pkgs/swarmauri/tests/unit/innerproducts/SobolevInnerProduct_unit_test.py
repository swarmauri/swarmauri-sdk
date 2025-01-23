import pytest
import numpy as np
from swarmauri.innerproducts.concrete.SobolevInnerProduct import SobolevInnerProduct
from swarmauri.vectors.concrete.Vector import Vector

# Test functions
def f(x):
    return x**2

def g(x):
    return x

def h(x):
    return np.sin(x)

@pytest.mark.unit
def test_ubc_type():
    """
    Test that the type attribute of SobolevInnerProduct is correctly set.
    """
    sobolev_inner_product = SobolevInnerProduct()
    assert sobolev_inner_product.type == 'SobolevInnerProduct'


@pytest.mark.unit
def test_resource_type():
    """
    Test that the resource attribute of SobolevInnerProduct is correctly set.
    """
    sobolev_inner_product = SobolevInnerProduct()
    assert sobolev_inner_product.resource == 'InnerProduct'


@pytest.mark.unit
def test_serialization():
    """
    Test that the SobolevInnerProduct instance can be serialized and deserialized correctly.
    """
    sobolev_inner_product = SobolevInnerProduct()
    serialized = sobolev_inner_product.model_dump_json()
    deserialized = SobolevInnerProduct.model_validate_json(serialized)

    assert sobolev_inner_product.id == deserialized.id


@pytest.mark.unit
def test_compute():
    """
    Test the Sobolev inner product computation for zeroth and first orders.
    """
    sobolev_inner_product = SobolevInnerProduct()

    # Zeroth-order test
    result_zeroth = sobolev_inner_product.compute(f, g, a=0, b=1, k=0)
    expected_zeroth = np.trapz([f(x) * g(x) for x in np.linspace(0, 1, 1000)], np.linspace(0, 1, 1000))
    assert pytest.approx(result_zeroth, 0.001) == expected_zeroth

    # First-order test
    result_first = sobolev_inner_product.compute(f, g, a=0, b=1, k=1)
    x_values = np.linspace(0, 1, 1000)
    f_derivative = 2 * x_values  # Derivative of f(x) = x^2
    g_derivative = np.ones_like(x_values)  # Derivative of g(x) = x
    expected_first = np.trapz([f(x) * g(x) for x in x_values], x_values) + \
                     np.trapz(f_derivative * g_derivative, x_values)
    assert pytest.approx(result_first, 0.001) == expected_first


@pytest.mark.unit
def test_zero():
    """
    Test that the Sobolev inner product is zero for zero functions.
    """
    zero_function = lambda x: 0
    sobolev_inner_product = SobolevInnerProduct()
    result = sobolev_inner_product.compute(zero_function, zero_function, a=0, b=1, k=2)
    assert result == 0.0


@pytest.mark.unit
def test_orthogonal():
    """
    Test the Sobolev inner product for orthogonal functions.
    """
    sobolev_inner_product = SobolevInnerProduct()

    def orthogonal_func1(x):
        return np.sin(x)

    def orthogonal_func2(x):
        return np.cos(x)

    result = sobolev_inner_product.compute(orthogonal_func1, orthogonal_func2, a=0, b=np.pi, k=0)
    assert pytest.approx(result, 0.001) == 0.0


@pytest.mark.unit
def test_negative_order():
    """
    Test that a ValueError is raised for negative derivative orders.
    """
    sobolev_inner_product = SobolevInnerProduct()
    with pytest.raises(ValueError):
        sobolev_inner_product.compute(f, g, a=0, b=1, k=-1)


@pytest.mark.unit
def test_invalid_interval():
    """
    Test that a ValueError is raised when the interval [a, b] is invalid.
    """
    sobolev_inner_product = SobolevInnerProduct()
    with pytest.raises(ValueError):
        sobolev_inner_product.compute(f, g, a=1, b=0)


@pytest.mark.unit
def test_check_conjugate_symmetry():
    """
    Test the conjugate symmetry property of the Sobolev inner product.
    """
    sobolev_inner_product = SobolevInnerProduct()
    result_fg = sobolev_inner_product.compute(f, g, a=0, b=1, k=1)
    result_gf = sobolev_inner_product.compute(g, f, a=0, b=1, k=1)

    assert pytest.approx(result_fg, 0.001) == pytest.approx(result_gf.conjugate())


@pytest.mark.unit
def test_check_linearity_first_argument():
    """
    Test the linearity in the first argument property of the Sobolev inner product.
    """
    sobolev_inner_product = SobolevInnerProduct()
    alpha = 2
    beta = 3

    def combined_func(x):
        return alpha * f(x) + beta * g(x)

    result_left = sobolev_inner_product.compute(combined_func, h, a=0, b=1, k=1)
    result_right = alpha * sobolev_inner_product.compute(f, h, a=0, b=1, k=1) + \
                   beta * sobolev_inner_product.compute(g, h, a=0, b=1, k=1)

    assert pytest.approx(result_left, 0.001) == pytest.approx(result_right)


@pytest.mark.unit
def test_check_positivity():
    """
    Test the positivity property of the Sobolev inner product.
    """
    sobolev_inner_product = SobolevInnerProduct()

    def zero_func(x):
        return 0

    result_nonzero = sobolev_inner_product.compute(f, f, a=0, b=1, k=2) > 0
    result_zero = sobolev_inner_product.compute(zero_func, zero_func, a=0, b=1, k=2) == 0

    assert result_nonzero
    assert result_zero


@pytest.mark.unit
def test_check_all_axioms():
    """
    Test all the axioms for the Sobolev inner product.
    """
    sobolev_inner_product = SobolevInnerProduct()
    alpha = 2
    u = lambda x: x
    v = lambda x: x**2
    w = lambda x: np.sin(x)

    conjugate_symmetry = sobolev_inner_product.compute(u, v, a=0, b=1, k=1) == \
                         np.conj(sobolev_inner_product.compute(v, u, a=0, b=1, k=1))
    linearity = sobolev_inner_product.compute(lambda x: alpha * u(x) + v(x), w, a=0, b=1, k=1) == \
                alpha * sobolev_inner_product.compute(u, w, a=0, b=1, k=1) + \
                sobolev_inner_product.compute(v, w, a=0, b=1, k=1)
    positivity = sobolev_inner_product.compute(u, u, a=0, b=1, k=2) > 0

    assert conjugate_symmetry
    assert linearity
    assert positivity

@pytest.mark.unit
def test_check_cauchy_schwarz_inequality():
    """
    Test the Cauchy-Schwarz inequality for the Sobolev inner product.
    """
    sobolev_inner_product = SobolevInnerProduct()
    a, b = 0, 1

    # Test with general functions
    result = sobolev_inner_product.check_cauchy_schwarz_inequality(f, g, a, b, k=1)
    assert result

    # Test with the zero function
    zero_function = lambda x: 0
    result_zero = sobolev_inner_product.check_cauchy_schwarz_inequality(f, zero_function, a, b, k=2)
    assert result_zero

    # Test with identical functions (Cauchy-Schwarz becomes equality)
    result_identical = sobolev_inner_product.check_cauchy_schwarz_inequality(f, f, a, b, k=1)
    assert result_identical

    # Test with orthogonal functions (Cauchy-Schwarz holds as inner product is zero)
    orthogonal_func1 = lambda x: np.sin(x)
    orthogonal_func2 = lambda x: np.cos(x)
    result_orthogonal = sobolev_inner_product.check_cauchy_schwarz_inequality(
        orthogonal_func1, orthogonal_func2, a=0, b=np.pi, k=0
    )
    assert result_orthogonal
