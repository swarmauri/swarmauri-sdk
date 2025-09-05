import logging
import math

import numpy as np
import pytest

from swarmauri_standard.similarities.TriangleCosineSimilarity import (
    TriangleCosineSimilarity,
)

# Set up logger
logger = logging.getLogger(__name__)


@pytest.fixture
def triangle_cosine_similarity():
    """
    Fixture that provides a TriangleCosineSimilarity instance.

    Returns
    -------
    TriangleCosineSimilarity
        An instance of the TriangleCosineSimilarity class
    """
    return TriangleCosineSimilarity()


@pytest.mark.unit
def test_initialization():
    """
    Test the initialization of TriangleCosineSimilarity.
    """
    similarity = TriangleCosineSimilarity()
    assert similarity.type == "TriangleCosineSimilarity"
    assert similarity.resource == "Similarity"


@pytest.mark.unit
def test_serialization(triangle_cosine_similarity):
    """
    Test serialization and deserialization of TriangleCosineSimilarity.

    Parameters
    ----------
    triangle_cosine_similarity : TriangleCosineSimilarity
        Fixture providing a TriangleCosineSimilarity instance
    """
    json_data = triangle_cosine_similarity.model_dump_json()
    deserialized = TriangleCosineSimilarity.model_validate_json(json_data)
    assert deserialized.type == triangle_cosine_similarity.type
    assert deserialized.resource == triangle_cosine_similarity.resource


@pytest.mark.unit
@pytest.mark.parametrize(
    "x, y, expected",
    [
        (np.array([1, 0, 0]), np.array([1, 0, 0]), 1.0),  # Same vector
        (
            np.array([1, 0, 0]),
            np.array([0, 1, 0]),
            0.5,
        ),  # Orthogonal vectors (90 degrees)
        (
            np.array([1, 0, 0]),
            np.array([-1, 0, 0]),
            0.0,
        ),  # Opposite vectors (180 degrees)
        (np.array([1, 1, 0]), np.array([1, 0, 0]), 0.75),  # 45 degree angle
        (
            np.array([1, 2, 3]),
            np.array([4, 5, 6]),
            0.9281,
        ),  # Arbitrary vectors - corrected value
    ],
)
def test_similarity(triangle_cosine_similarity, x, y, expected):
    """
    Test the similarity method with various vector pairs.

    Parameters
    ----------
    triangle_cosine_similarity : TriangleCosineSimilarity
        Fixture providing a TriangleCosineSimilarity instance
    x : np.ndarray
        First vector
    y : np.ndarray
        Second vector
    expected : float
        Expected similarity value
    """
    result = triangle_cosine_similarity.similarity(x, y)
    assert pytest.approx(result, abs=1e-4) == expected


@pytest.mark.unit
def test_similarity_with_lists(triangle_cosine_similarity):
    """
    Test the similarity method with list inputs.

    Parameters
    ----------
    triangle_cosine_similarity : TriangleCosineSimilarity
        Fixture providing a TriangleCosineSimilarity instance
    """
    result = triangle_cosine_similarity.similarity([1, 0, 0], [0, 1, 0])
    assert pytest.approx(result, abs=1e-10) == 0.5


@pytest.mark.unit
def test_similarities(triangle_cosine_similarity):
    """
    Test the similarities method with multiple vectors.

    Parameters
    ----------
    triangle_cosine_similarity : TriangleCosineSimilarity
        Fixture providing a TriangleCosineSimilarity instance
    """
    x = np.array([1, 0, 0])
    ys = [
        np.array([1, 0, 0]),  # Same vector
        np.array([0, 1, 0]),  # Orthogonal
        np.array([-1, 0, 0]),  # Opposite
    ]
    expected = [1.0, 0.5, 0.0]

    results = triangle_cosine_similarity.similarities(x, ys)
    assert len(results) == len(expected)
    for res, exp in zip(results, expected):
        assert pytest.approx(res, abs=1e-10) == exp


@pytest.mark.unit
def test_dissimilarity(triangle_cosine_similarity):
    """
    Test the dissimilarity method.

    Parameters
    ----------
    triangle_cosine_similarity : TriangleCosineSimilarity
        Fixture providing a TriangleCosineSimilarity instance
    """
    x = np.array([1, 0, 0])
    y = np.array([0, 1, 0])

    similarity = triangle_cosine_similarity.similarity(x, y)
    dissimilarity = triangle_cosine_similarity.dissimilarity(x, y)

    assert pytest.approx(dissimilarity, abs=1e-10) == 1.0 - similarity
    assert pytest.approx(dissimilarity, abs=1e-10) == 0.5


@pytest.mark.unit
def test_check_bounded(triangle_cosine_similarity):
    """
    Test the check_bounded method.

    Parameters
    ----------
    triangle_cosine_similarity : TriangleCosineSimilarity
        Fixture providing a TriangleCosineSimilarity instance
    """
    assert triangle_cosine_similarity.check_bounded() is True


@pytest.mark.unit
def test_check_reflexivity(triangle_cosine_similarity):
    """
    Test the check_reflexivity method.

    Parameters
    ----------
    triangle_cosine_similarity : TriangleCosineSimilarity
        Fixture providing a TriangleCosineSimilarity instance
    """
    x = np.array([1, 2, 3])
    assert triangle_cosine_similarity.check_reflexivity(x) is True


@pytest.mark.unit
def test_check_symmetry(triangle_cosine_similarity):
    """
    Test the check_symmetry method.

    Parameters
    ----------
    triangle_cosine_similarity : TriangleCosineSimilarity
        Fixture providing a TriangleCosineSimilarity instance
    """
    x = np.array([1, 2, 3])
    y = np.array([4, 5, 6])
    assert triangle_cosine_similarity.check_symmetry(x, y) is True


@pytest.mark.unit
def test_validate_vector_with_valid_input(triangle_cosine_similarity):
    """
    Test the _validate_vector method with valid input.

    Parameters
    ----------
    triangle_cosine_similarity : TriangleCosineSimilarity
        Fixture providing a TriangleCosineSimilarity instance
    """
    x = np.array([1, 2, 3])
    validated = triangle_cosine_similarity._validate_vector(x)
    assert np.array_equal(validated, x)


@pytest.mark.unit
def test_validate_vector_with_zero_vector(triangle_cosine_similarity):
    """
    Test the _validate_vector method with a zero vector.

    Parameters
    ----------
    triangle_cosine_similarity : TriangleCosineSimilarity
        Fixture providing a TriangleCosineSimilarity instance
    """
    with pytest.raises(ValueError, match="Zero vectors are not allowed"):
        triangle_cosine_similarity._validate_vector(np.array([0, 0, 0]))


@pytest.mark.unit
def test_validate_vector_with_scalar(triangle_cosine_similarity):
    """
    Test the _validate_vector method with a scalar.

    Parameters
    ----------
    triangle_cosine_similarity : TriangleCosineSimilarity
        Fixture providing a TriangleCosineSimilarity instance
    """
    with pytest.raises(ValueError, match="Input must be a vector, not a scalar"):
        triangle_cosine_similarity._validate_vector(np.array(5))


@pytest.mark.unit
def test_similarity_with_incompatible_dimensions(triangle_cosine_similarity):
    """
    Test the similarity method with vectors of incompatible dimensions.

    Parameters
    ----------
    triangle_cosine_similarity : TriangleCosineSimilarity
        Fixture providing a TriangleCosineSimilarity instance
    """
    x = np.array([1, 2, 3])
    y = np.array([1, 2])

    with pytest.raises(ValueError, match="Incompatible dimensions"):
        triangle_cosine_similarity.similarity(x, y)


@pytest.mark.unit
def test_angle_calculation():
    """
    Test that the angle calculation in the similarity method is correct.
    """
    similarity = TriangleCosineSimilarity()

    # Test vectors with a known angle (45 degrees)
    x = np.array([1, 0])
    y = np.array([1, 1])

    # Calculate expected similarity
    angle_rad = math.pi / 4  # 45 degrees in radians
    expected_similarity = 1.0 - (angle_rad / math.pi)

    result = similarity.similarity(x, y)
    assert pytest.approx(result, abs=1e-10) == expected_similarity


@pytest.mark.unit
def test_similarity_edge_cases(triangle_cosine_similarity):
    """
    Test similarity method with edge cases.

    Parameters
    ----------
    triangle_cosine_similarity : TriangleCosineSimilarity
        Fixture providing a TriangleCosineSimilarity instance
    """
    # Almost parallel vectors
    x = np.array([1, 0, 0])
    y = np.array([0.9999, 0.0001, 0])
    result = triangle_cosine_similarity.similarity(x, y)
    assert result > 0.99

    # Almost opposite vectors
    y = np.array([-0.9999, -0.0001, 0])
    result = triangle_cosine_similarity.similarity(x, y)
    assert result < 0.01


@pytest.mark.unit
def test_similarities_with_errors(triangle_cosine_similarity):
    """
    Test the similarities method when some comparisons raise errors.

    Parameters
    ----------
    triangle_cosine_similarity : TriangleCosineSimilarity
        Fixture providing a TriangleCosineSimilarity instance
    """
    x = np.array([1, 0, 0])
    ys = [
        np.array([1, 0, 0]),  # Valid
        np.array([0, 0, 0]),  # Zero vector (invalid)
        np.array([0, 1]),  # Incompatible dimensions (invalid)
    ]

    results = triangle_cosine_similarity.similarities(x, ys)
    assert len(results) == 3
    assert pytest.approx(results[0], abs=1e-10) == 1.0
    assert math.isnan(results[1])
    assert math.isnan(results[2])
