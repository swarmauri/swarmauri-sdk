import pytest
from math import isclose, acos, pi
from swarmauri.norms.concrete.EuclideanNorm import EuclideanNorm
from swarmauri.vectors.concrete.Vector import Vector

@pytest.mark.unit
def test_ubc_type():
    """
    Test that the type attribute of EuclideanNorm is correctly set.
    """
    norm = EuclideanNorm()
    assert norm.type == "EuclideanNorm"


@pytest.mark.unit
def test_resource_type():
    """
    Test that the resource attribute of EuclideanNorm is correctly set.
    """
    norm = EuclideanNorm()
    assert norm.resource == "Norm"


@pytest.mark.unit
def test_serialization():
    """
    Test that the EuclideanNorm instance can be serialized and deserialized correctly.
    """
    norm = EuclideanNorm()
    serialized = norm.model_dump_json()
    deserialized = EuclideanNorm.model_validate_json(serialized)

    assert norm.id == deserialized.id


@pytest.mark.unit
def test_compute():
    """
    Test the computation of the Euclidean norm.
    """
    vector = Vector(value=[3, 4])
    norm = EuclideanNorm()
    expected_result = (3**2 + 4**2) ** 0.5  # sqrt(3^2 + 4^2)
    assert pytest.approx(norm.compute(vector)) == expected_result


@pytest.mark.unita
def test_zero_vector():
    """
    Test that the Euclidean norm of a zero vector is zero.
    """
    vector = Vector(value=[0, 0, 0])
    norm = EuclideanNorm()
    assert norm.compute(vector) == 0.0


@pytest.mark.unit
def test_verify_definiteness():
    """
    Test the definiteness property of the Euclidean norm.
    Ensure ∥x∥ = 0 ⟺ x = 0.
    """
    norm = EuclideanNorm()

    # Test for zero vector
    zero_vector = Vector(value=[0, 0, 0])
    assert norm.compute(zero_vector) == 0.0  # Norm is zero
    assert norm.verify_definiteness(zero_vector)  # Satisfies definiteness

    # Test for non-zero vector
    non_zero_vector = Vector(value=[1, 2, 3])
    assert norm.compute(non_zero_vector) > 0  # Norm is positive
    assert norm.verify_definiteness(non_zero_vector)  # Satisfies definiteness


@pytest.mark.unit
def test_non_negativity():
    """
    Test the non-negativity property of the Euclidean norm.
    """
    vector = Vector(value=[-3, -4])
    norm = EuclideanNorm()
    assert norm.compute(vector) >= 0


@pytest.mark.unit
def test_absolute_scalability():
    """
    Test the absolute scalability property of the Euclidean norm.
    """
    vector = Vector(value=[1, 2, 2])
    alpha = -3
    norm = EuclideanNorm()
    norm_alpha_x = norm.compute(Vector(value=[alpha * v for v in vector.value]))
    expected_result = abs(alpha) * norm.compute(vector)
    assert pytest.approx(norm_alpha_x) == pytest.approx(expected_result)


@pytest.mark.unit
def test_triangle_inequality():
    """
    Test the triangle inequality property of the Euclidean norm.
    """
    vector1 = Vector(value=[3, 4])
    vector2 = Vector(value=[1, 2])
    norm = EuclideanNorm()
    combined_vector = Vector(value=[vector1.value[i] + vector2.value[i] for i in range(len(vector1.value))])

    norm_combined = norm.compute(combined_vector)
    norm1 = norm.compute(vector1)
    norm2 = norm.compute(vector2)

    assert norm_combined <= norm1 + norm2


@pytest.mark.unit
def test_angle_between_vectors():
    """
    Test the angle computation between two vectors using EuclideanNorm.
    """
    vector1 = Vector(value=[1, 0])
    vector2 = Vector(value=[0, 1])
    norm = EuclideanNorm()

    angle = norm.angle_between_vectors(vector1, vector2)
    assert pytest.approx(angle) == pytest.approx(pi / 2)  # 90 degrees


@pytest.mark.unit
def test_verify_orthogonality():
    """
    Test the orthogonality check of two vectors.
    """
    vector1 = Vector(value=[1, 0])
    vector2 = Vector(value=[0, 1])
    norm = EuclideanNorm()

    assert norm.verify_orthogonality(vector1, vector2)


@pytest.mark.unit
def test_project():
    """
    Test the projection of one vector onto another.
    """
    vector1 = Vector(value=[3, 4])
    vector2 = Vector(value=[1, 0])  # Unit vector along x-axis
    norm = EuclideanNorm()

    projection = norm.project(vector1, vector2)
    expected_projection = Vector(value=[3, 0])  # Project onto x-axis
    assert projection.value == expected_projection.value


@pytest.mark.unit
def test_verify_parallelogram_law():
    """
    Test the verification of the parallelogram law.
    """
    vector1 = Vector(value=[1, 2])
    vector2 = Vector(value=[3, 4])
    norm = EuclideanNorm()

    # Should pass without raising ValueError
    norm.verify_parallelogram_law(vector1, vector2)


@pytest.mark.unit
def test_check_all_norm_axioms():
    """
    Test all norm axioms: non-negativity, definiteness, absolute scalability, and triangle inequality
    using the check_all_norm_axioms method.
    """
    vector1 = Vector(value=[3, 4])
    vector2 = Vector(value=[1, 2])
    alpha = -2
    norm = EuclideanNorm()

    # Use the check_all_norm_axioms method
    assert norm.check_all_norm_axioms(alpha, vector1, vector2)
