import logging

import numpy as np
import pytest

from swarmauri_standard.similarities.TanimotoSimilarity import TanimotoSimilarity

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.fixture
def tanimoto_similarity():
    """
    Fixture that provides a TanimotoSimilarity instance.

    Returns
    -------
    TanimotoSimilarity
        An instance of the TanimotoSimilarity class
    """
    return TanimotoSimilarity()


@pytest.mark.unit
def test_initialization():
    """Test that TanimotoSimilarity initializes correctly."""
    similarity = TanimotoSimilarity()
    assert similarity.type == "TanimotoSimilarity"
    assert similarity.resource == "Similarity"


@pytest.mark.unit
def test_type_attribute():
    """Test that the type attribute is correctly set."""
    similarity = TanimotoSimilarity()
    assert similarity.type == "TanimotoSimilarity"


@pytest.mark.unit
class TestValidation:
    """Tests for input validation in TanimotoSimilarity."""

    @pytest.mark.unit
    def test_validate_input_valid(self, tanimoto_similarity):
        """Test validation with valid inputs."""
        x = [1, 2, 3]
        y = [4, 5, 6]
        x_array, y_array = tanimoto_similarity._validate_input(x, y)
        assert isinstance(x_array, np.ndarray)
        assert isinstance(y_array, np.ndarray)
        np.testing.assert_array_equal(x_array, np.array([1, 2, 3]))
        np.testing.assert_array_equal(y_array, np.array([4, 5, 6]))

    @pytest.mark.unit
    def test_validate_input_different_dimensions(self, tanimoto_similarity):
        """Test validation with inputs of different dimensions."""
        x = [1, 2, 3]
        y = [4, 5]
        with pytest.raises(
            ValueError, match="Input vectors must have the same dimensions"
        ):
            tanimoto_similarity._validate_input(x, y)

    @pytest.mark.unit
    def test_validate_input_zero_vectors(self, tanimoto_similarity):
        """Test validation with zero vectors."""
        x = [0, 0, 0]
        y = [1, 2, 3]
        with pytest.raises(
            ValueError, match="Tanimoto similarity is not defined for zero vectors"
        ):
            tanimoto_similarity._validate_input(x, y)

        x = [1, 2, 3]
        y = [0, 0, 0]
        with pytest.raises(
            ValueError, match="Tanimoto similarity is not defined for zero vectors"
        ):
            tanimoto_similarity._validate_input(x, y)


@pytest.mark.unit
class TestSimilarity:
    """Tests for the similarity calculation in TanimotoSimilarity."""

    @pytest.mark.parametrize(
        "x, y, expected",
        [
            ([1, 1, 1], [1, 1, 1], 1.0),  # Identical vectors
            ([1, 0, 0], [0, 1, 0], 0.0),  # Orthogonal vectors
            ([1, 1, 0], [1, 1, 1], 2 / 3),  # Partial overlap
            ([1, 2, 3], [2, 4, 6], 1.0),  # Proportional vectors
            (
                [0.5, 0.5],
                [0.25, 0.75],
                0.8,
            ),  # Real-valued vectors - corrected expected value
        ],
    )
    def test_similarity_calculation(self, tanimoto_similarity, x, y, expected):
        """Test similarity calculation with various inputs."""
        result = tanimoto_similarity.similarity(x, y)
        assert abs(result - expected) < 1e-10

    @pytest.mark.unit
    def test_similarity_error_handling(self, tanimoto_similarity):
        """Test error handling in similarity calculation."""
        with pytest.raises(ValueError):
            tanimoto_similarity.similarity([1, 2], [1, 2, 3])  # Different dimensions

        with pytest.raises(ValueError):
            tanimoto_similarity.similarity([0, 0, 0], [1, 2, 3])  # Zero vector

    @pytest.mark.unit
    def test_similarity_with_numpy_arrays(self, tanimoto_similarity):
        """Test similarity calculation with numpy arrays as input."""
        x = np.array([1, 2, 3])
        y = np.array([4, 5, 6])
        result = tanimoto_similarity.similarity(x, y)
        # Expected: (1*4 + 2*5 + 3*6) / (14 + 77 - 32) = 32 / 59
        expected = 32 / 59
        assert abs(result - expected) < 1e-10


@pytest.mark.unit
class TestSimilarities:
    """Tests for the similarities method in TanimotoSimilarity."""

    @pytest.mark.unit
    def test_similarities_calculation(self, tanimoto_similarity):
        """Test calculation of multiple similarities."""
        x = [1, 1, 1]
        ys = [[1, 1, 1], [1, 0, 0], [0, 1, 0], [0, 0, 1]]
        results = tanimoto_similarity.similarities(x, ys)
        expected = [1.0, 1 / 3, 1 / 3, 1 / 3]
        assert len(results) == len(expected)
        for res, exp in zip(results, expected):
            assert abs(res - exp) < 1e-10

    @pytest.mark.unit
    def test_similarities_with_errors(self, tanimoto_similarity):
        """Test handling of errors in multiple similarity calculations."""
        x = [1, 1, 1]
        ys = [
            [1, 1, 1],
            [1, 0],
            [0, 0, 0],
        ]  # Second item has wrong dimension, third is zero vector

        # The method should handle errors for individual comparisons
        results = tanimoto_similarity.similarities(x, ys)
        assert not np.isnan(results[0])  # First comparison should succeed
        assert np.isnan(results[1])  # Second comparison should fail with NaN
        assert np.isnan(results[2])  # Third comparison should fail with NaN


@pytest.mark.unit
class TestDissimilarity:
    """Tests for the dissimilarity calculation in TanimotoSimilarity."""

    @pytest.mark.parametrize(
        "x, y, expected",
        [
            ([1, 1, 1], [1, 1, 1], 0.0),  # Identical vectors
            ([1, 0, 0], [0, 1, 0], 1.0),  # Orthogonal vectors
            ([1, 1, 0], [1, 1, 1], 1 / 3),  # Partial overlap
        ],
    )
    def test_dissimilarity_calculation(self, tanimoto_similarity, x, y, expected):
        """Test dissimilarity calculation with various inputs."""
        result = tanimoto_similarity.dissimilarity(x, y)
        assert abs(result - expected) < 1e-10


@pytest.mark.unit
class TestProperties:
    """Tests for the mathematical properties of TanimotoSimilarity."""

    @pytest.mark.unit
    def test_bounded(self, tanimoto_similarity):
        """Test that TanimotoSimilarity is bounded."""
        assert tanimoto_similarity.check_bounded() is True

    @pytest.mark.parametrize("x", [[1, 2, 3], [0.5, 0.5, 0.5], [10, 20, 30, 40]])
    def test_reflexivity(self, tanimoto_similarity, x):
        """Test that TanimotoSimilarity is reflexive."""
        assert tanimoto_similarity.check_reflexivity(x)

    @pytest.mark.parametrize(
        "x, y",
        [
            ([1, 2, 3], [4, 5, 6]),
            ([0.5, 0.5], [0.25, 0.75]),
            ([10, 20, 30, 40], [1, 2, 3, 4]),
        ],
    )
    def test_symmetry(self, tanimoto_similarity, x, y):
        """Test that TanimotoSimilarity is symmetric."""
        assert tanimoto_similarity.check_symmetry(x, y)

    @pytest.mark.parametrize(
        "x, y",
        [
            ([1, 2, 3], [2, 4, 6]),  # Proportional vectors
            ([1, 1, 1], [2, 2, 2]),  # Proportional vectors
            ([1, 2, 3], [3, 2, 1]),  # Non-proportional vectors
        ],
    )
    def test_identity_of_discernibles(self, tanimoto_similarity, x, y):
        """Test identity of discernibles property."""
        assert tanimoto_similarity.check_identity_of_discernibles(x, y) is True

    @pytest.mark.unit
    def test_identity_of_discernibles_proportional(self, tanimoto_similarity):
        """Test that proportional vectors have similarity 1."""
        x = [1, 2, 3]
        y = [2, 4, 6]  # y = 2*x
        similarity = tanimoto_similarity.similarity(x, y)
        assert abs(similarity - 1.0) < 1e-10
        assert tanimoto_similarity.check_identity_of_discernibles(x, y) is True
