import logging
from typing import List

import numpy as np
import pytest

from swarmauri_standard.similarities.BrayCurtisSimilarity import BrayCurtisSimilarity

# Set up logger
logger = logging.getLogger(__name__)


@pytest.fixture
def bray_curtis_similarity() -> BrayCurtisSimilarity:
    """
    Fixture that returns a BrayCurtisSimilarity instance.

    Returns
    -------
    BrayCurtisSimilarity
        An instance of BrayCurtisSimilarity
    """
    return BrayCurtisSimilarity()


@pytest.mark.unit
def test_type(bray_curtis_similarity):
    """
    Test that the type attribute is correctly set.
    """
    assert bray_curtis_similarity.type == "BrayCurtisSimilarity"


@pytest.mark.unit
def test_init(bray_curtis_similarity: BrayCurtisSimilarity):
    """
    Test initialization of BrayCurtisSimilarity.

    Parameters
    ----------
    bray_curtis_similarity : BrayCurtisSimilarity
        The BrayCurtisSimilarity instance
    """
    assert isinstance(bray_curtis_similarity, BrayCurtisSimilarity)


@pytest.mark.unit
@pytest.mark.parametrize(
    "x, y, expected_similarity",
    [
        ([1, 2, 3], [1, 2, 3], 1.0),  # Identical vectors
        ([0, 0, 0], [0, 0, 0], 1.0),  # All zeros
        ([1, 2, 3], [3, 2, 1], 0.6666666666666667),  # Reversed
        ([4, 0, 0], [0, 5, 0], 0.0),  # No overlap
        ([1, 1, 1], [2, 2, 2], 0.6666666666666667),  # Proportional
        ([0.5, 1.5, 2.5], [0.5, 1.5, 2.5], 1.0),  # Identical with floats
    ],
)
def test_similarity(
    bray_curtis_similarity: BrayCurtisSimilarity,
    x: List[float],
    y: List[float],
    expected_similarity: float,
):
    """
    Test the similarity method with various inputs.

    Parameters
    ----------
    bray_curtis_similarity : BrayCurtisSimilarity
        The BrayCurtisSimilarity instance
    x : List[float]
        First vector
    y : List[float]
        Second vector
    expected_similarity : float
        Expected similarity value
    """
    result = bray_curtis_similarity.similarity(x, y)
    assert pytest.approx(result, abs=1e-10) == expected_similarity


@pytest.mark.unit
def test_similarity_with_numpy_arrays(bray_curtis_similarity: BrayCurtisSimilarity):
    """
    Test the similarity method with numpy arrays.

    Parameters
    ----------
    bray_curtis_similarity : BrayCurtisSimilarity
        The BrayCurtisSimilarity instance
    """
    x = np.array([1, 2, 3])
    y = np.array([2, 2, 2])
    result = bray_curtis_similarity.similarity(x, y)
    expected = 0.8333333333333334  # (1 - 2/12)
    assert pytest.approx(result, abs=1e-10) == expected


@pytest.mark.unit
def test_similarity_with_negative_values(bray_curtis_similarity: BrayCurtisSimilarity):
    """
    Test that similarity method raises ValueError for negative values.

    Parameters
    ----------
    bray_curtis_similarity : BrayCurtisSimilarity
        The BrayCurtisSimilarity instance
    """
    with pytest.raises(
        ValueError, match="Bray-Curtis similarity requires non-negative input values"
    ):
        bray_curtis_similarity.similarity([1, -2, 3], [1, 2, 3])

    with pytest.raises(
        ValueError, match="Bray-Curtis similarity requires non-negative input values"
    ):
        bray_curtis_similarity.similarity([1, 2, 3], [1, -2, 3])


@pytest.mark.unit
def test_similarity_with_different_shapes(bray_curtis_similarity: BrayCurtisSimilarity):
    """
    Test that similarity method raises ValueError for inputs with different shapes.

    Parameters
    ----------
    bray_curtis_similarity : BrayCurtisSimilarity
        The BrayCurtisSimilarity instance
    """
    with pytest.raises(ValueError, match="Input vectors must have the same shape"):
        bray_curtis_similarity.similarity([1, 2, 3], [1, 2])


@pytest.mark.unit
def test_similarity_with_invalid_types(bray_curtis_similarity: BrayCurtisSimilarity):
    """
    Test that similarity method raises TypeError for inputs that cannot be converted to numeric arrays.

    Parameters
    ----------
    bray_curtis_similarity : BrayCurtisSimilarity
        The BrayCurtisSimilarity instance
    """
    with pytest.raises(Exception):
        bray_curtis_similarity.similarity("not a vector", [1, 2, 3])


@pytest.mark.unit
def test_similarities(bray_curtis_similarity: BrayCurtisSimilarity):
    """
    Test the similarities method.

    Parameters
    ----------
    bray_curtis_similarity : BrayCurtisSimilarity
        The BrayCurtisSimilarity instance
    """
    x = [1, 2, 3]
    ys = [[1, 2, 3], [0, 0, 0], [3, 2, 1]]
    results = bray_curtis_similarity.similarities(x, ys)

    expected = [1.0, 0.0, 0.6666666666666667]
    assert len(results) == len(expected)
    for result, exp in zip(results, expected):
        assert pytest.approx(result, abs=1e-10) == exp


@pytest.mark.unit
def test_similarities_with_invalid_inputs(bray_curtis_similarity: BrayCurtisSimilarity):
    """
    Test the similarities method with invalid inputs.

    Parameters
    ----------
    bray_curtis_similarity : BrayCurtisSimilarity
        The BrayCurtisSimilarity instance
    """
    # Test with negative values
    with pytest.raises(
        ValueError, match="Bray-Curtis similarity requires non-negative input values"
    ):
        bray_curtis_similarity.similarities([1, -2, 3], [[1, 2, 3]])

    # Test with different shapes
    with pytest.raises(ValueError, match="Input vectors must have the same shape"):
        bray_curtis_similarity.similarities([1, 2, 3], [[1, 2], [3, 4]])


@pytest.mark.unit
def test_dissimilarity(bray_curtis_similarity: BrayCurtisSimilarity):
    """
    Test the dissimilarity method.

    Parameters
    ----------
    bray_curtis_similarity : BrayCurtisSimilarity
        The BrayCurtisSimilarity instance
    """
    x = [1, 2, 3]
    y = [3, 2, 1]

    # Dissimilarity should be 1 - similarity
    similarity = bray_curtis_similarity.similarity(x, y)
    dissimilarity = bray_curtis_similarity.dissimilarity(x, y)

    assert pytest.approx(dissimilarity, abs=1e-10) == 1.0 - similarity
    assert pytest.approx(dissimilarity, abs=1e-10) == 0.3333333333333333


@pytest.mark.unit
def test_check_bounded(bray_curtis_similarity: BrayCurtisSimilarity):
    """
    Test the check_bounded method.

    Parameters
    ----------
    bray_curtis_similarity : BrayCurtisSimilarity
        The BrayCurtisSimilarity instance
    """
    assert bray_curtis_similarity.check_bounded() is True


@pytest.mark.unit
def test_check_symmetry(bray_curtis_similarity: BrayCurtisSimilarity):
    """
    Test the check_symmetry method.

    Parameters
    ----------
    bray_curtis_similarity : BrayCurtisSimilarity
        The BrayCurtisSimilarity instance
    """
    x = [1, 2, 3]
    y = [3, 2, 1]

    assert bray_curtis_similarity.check_symmetry(x, y) is True


@pytest.mark.unit
def test_serialization(bray_curtis_similarity: BrayCurtisSimilarity):
    """
    Test serialization and deserialization of BrayCurtisSimilarity.

    Parameters
    ----------
    bray_curtis_similarity : BrayCurtisSimilarity
        The BrayCurtisSimilarity instance
    """
    # Serialize to JSON
    json_data = bray_curtis_similarity.model_dump_json()

    # Deserialize from JSON
    deserialized = BrayCurtisSimilarity.model_validate_json(json_data)

    # Verify type is preserved
    assert deserialized.type == "BrayCurtisSimilarity"

    # Test functionality is preserved
    x = [1, 2, 3]
    y = [3, 2, 1]
    original_result = bray_curtis_similarity.similarity(x, y)
    deserialized_result = deserialized.similarity(x, y)

    assert pytest.approx(original_result, abs=1e-10) == deserialized_result
