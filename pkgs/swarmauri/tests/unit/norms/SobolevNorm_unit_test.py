import pytest
import numpy as np
from swarmauri.norms.concrete.SobolevNorm import SobolevNorm
from swarmauri.innerproducts.concrete.SobolevInnerProduct import SobolevInnerProduct
from swarmauri.vectors.concrete.Vector import Vector

# Example test functions
def f(x):
    return x**2

def g(x):
    return x

def h(x):
    return np.sin(x)

@pytest.mark.unit
def test_ubc_type():
    """
    Test that the type attribute of SobolevNorm is correctly set.
    """
    norm = SobolevNorm()
    assert norm.type == "SobolevNorm"


@pytest.mark.unit
def test_resource_type():
    """
    Test that the resource attribute of SobolevNorm is correctly set.
    """
    norm = SobolevNorm()
    assert norm.resource == "Norm"


@pytest.mark.unit
def test_compute_zeroth_order():
    """
    Test the computation of the Sobolev norm for zeroth-order Sobolev inner product.
    """
    norm = SobolevNorm()
    result = norm.compute(f=f, a=0, b=1, k=0, num_points=1000)

    # Manually compute the expected result for zeroth-order
    x_values = np.linspace(0, 1, 1000)
    expected_inner_product = np.trapz([f(x)**2 for x in x_values], x_values)
    expected_norm = np.sqrt(expected_inner_product)

    assert pytest.approx(result, 0.001) == expected_norm


@pytest.mark.unit
def test_compute_first_order():
    """
    Test the computation of the Sobolev norm for first-order Sobolev inner product.
    """
    norm = SobolevNorm()
    result = norm.compute(f=f, a=0, b=1, k=1, num_points=1000)

    # Manually compute the expected result for first-order
    x_values = np.linspace(0, 1, 1000)
    f_values = np.array([f(x) for x in x_values])
    f_derivative = np.gradient(f_values, x_values)

    inner_product_function = np.trapz(f_values**2, x_values)
    inner_product_derivative = np.trapz(f_derivative**2, x_values)
    expected_inner_product = inner_product_function + inner_product_derivative
    expected_norm = np.sqrt(expected_inner_product)

    assert pytest.approx(result, 0.001) == expected_norm


@pytest.mark.unit
def test_zero_function():
    """
    Test that the Sobolev norm of a zero function is zero.
    """
    norm = SobolevNorm()
    zero_function = lambda x: 0
    result = norm.compute(f=zero_function, a=0, b=1, k=2, num_points=1000)

    assert result == 0.0


@pytest.mark.unit
def test_non_negativity():
    """
    Test the non-negativity property of the Sobolev norm.
    """
    norm = SobolevNorm()
    result = norm.compute(f=f, a=0, b=1, k=1, num_points=1000)

    assert result >= 0


@pytest.mark.unit
def test_absolute_scalability():
    """
    Test the absolute scalability property of the Sobolev norm.
    """
    norm = SobolevNorm()
    alpha = -2

    def scaled_function(x):
        return alpha * f(x)

    norm_original = norm.compute(f=f, a=0, b=1, k=1, num_points=1000)
    norm_scaled = norm.compute(f=scaled_function, a=0, b=1, k=1, num_points=1000)
    assert pytest.approx(norm_scaled) == abs(alpha) * norm_original


@pytest.mark.unit
def test_triangle_inequality():
    """
    Test the triangle inequality property of the Sobolev norm.
    """
    norm = SobolevNorm()

    def combined_function(x):
        return f(x) + g(x)

    norm_combined = norm.compute(f=combined_function, a=0, b=1, k=1, num_points=1000)
    norm_f = norm.compute(f=f, a=0, b=1, k=1, num_points=1000)
    norm_g = norm.compute(f=g, a=0, b=1, k=1, num_points=1000)

    assert norm_combined <= norm_f + norm_g


@pytest.mark.unit
def test_verify_parallelogram_law():
    """
    Test the verification of the parallelogram law.
    """
    norm = SobolevNorm()

    def function1(x):
        return x**2

    def function2(x):
        return np.sin(x)

    # Should pass without raising ValueError
    norm.verify_parallelogram_law(function1, function2)


@pytest.mark.unit
def test_angle_between_functions():
    """
    Test the angle computation between two functions using SobolevNorm.
    """
    norm = SobolevNorm()
    angle = norm.angle_between_vectors(f, g)
    assert pytest.approx(angle, 0.01) == np.pi / 4  # Expected ~45 degrees


@pytest.mark.unit
def test_verify_orthogonality():
    """
    Test the orthogonality check of two functions.
    """
    norm = SobolevNorm()

    def orthogonal_f(x):
        return np.sin(x)

    def orthogonal_g(x):
        return np.cos(x)

    # Verify orthogonality
    assert norm.verify_orthogonality(orthogonal_f, orthogonal_g)


@pytest.mark.unit
def test_project():
    """
    Test the projection of one function onto another.
    """
    norm = SobolevNorm()

    def f1(x):
        return x**2

    def f2(x):
        return 1

    # Project f1 onto f2
    projection = norm.project(f1, f2)

    # Expected projection is proportional to f2
    def expected_projection(x):
        return np.trapz([f1(xi) * f2(xi) for xi in np.linspace(0, 1, 1000)]) / \
               np.trapz([f2(xi)**2 for xi in np.linspace(0, 1, 1000)]) * f2(x)

    x_values = np.linspace(0, 1, 100)
    for x in x_values:
        assert pytest.approx(projection(x)) == pytest.approx(expected_projection(x))


@pytest.mark.unit
def test_check_all_norm_axioms():
    """
    Test all norm axioms: non-negativity, absolute scalability, and triangle inequality using check_all_norm_axioms.
    """
    norm = SobolevNorm()
    alpha = -2

    def f_func(x):
        return x**2

    def g_func(x):
        return x

    # Convert functions to `Vector` for compatibility
    vector_f = Vector(value=f_func, domain=(0, 1), num_samples=100)
    vector_g = Vector(value=g_func, domain=(0, 1), num_samples=100)

    # Check all norm axioms using the method provided by NormBase
    assert norm.check_all_norm_axioms(alpha, vector_f, vector_g)
