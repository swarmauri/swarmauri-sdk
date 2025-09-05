import logging

import numpy as np
import pytest

from swarmauri_standard.similarities.HellingerAffinitySimilarity import (
    HellingerAffinitySimilarity,
)

# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.fixture
def hellingeraffinitysimilarity():
    """
    Fixture that returns a HellingerAffinitySimilarity instance.

    Returns
    -------
    HellingerAffinitySimilarity
        An instance of the HellingerAffinitySimilarity class
    """
    return HellingerAffinitySimilarity()


@pytest.mark.unit
def test_type(hellingeraffinitysimilarity):
    """Test that the type attribute is correctly set."""
    assert hellingeraffinitysimilarity.type == "HellingerAffinitySimilarity"


@pytest.mark.unit
def test_initialization(hellingeraffinitysimilarity):
    """Test that the class initializes correctly."""
    assert isinstance(hellingeraffinitysimilarity, HellingerAffinitySimilarity)


@pytest.mark.unit
class TestValidation:
    """Tests for the validation functionality."""

    def test_valid_probability_vector(self, hellingeraffinitysimilarity):
        """Test validation of a valid probability vector."""
        vec = np.array([0.2, 0.3, 0.5])
        validated = hellingeraffinitysimilarity._validate_probability_vector(vec)
        assert np.array_equal(validated, vec)

    def test_negative_values(self, hellingeraffinitysimilarity):
        """Test validation with negative values."""
        vec = np.array([0.2, -0.3, 1.1])
        with pytest.raises(
            ValueError, match="All values in probability vector must be non-negative"
        ):
            hellingeraffinitysimilarity._validate_probability_vector(vec)

    def test_sum_not_one(self, hellingeraffinitysimilarity):
        """Test validation when sum is not 1."""
        vec = np.array([0.2, 0.3, 0.6])  # Sum is 1.1
        with pytest.raises(ValueError, match="Probability vector must sum to 1"):
            hellingeraffinitysimilarity._validate_probability_vector(vec)

    def test_list_conversion(self, hellingeraffinitysimilarity):
        """Test validation converts list to numpy array."""
        vec = [0.2, 0.3, 0.5]
        validated = hellingeraffinitysimilarity._validate_probability_vector(vec)
        assert isinstance(validated, np.ndarray)
        assert np.array_equal(validated, np.array(vec))


@pytest.mark.unit
class TestSimilarity:
    """Tests for the similarity calculation."""

    @pytest.mark.parametrize(
        "x, y, expected",
        [
            (np.array([1.0, 0.0]), np.array([1.0, 0.0]), 1.0),  # Same distributions
            (np.array([0.5, 0.5]), np.array([0.5, 0.5]), 1.0),  # Same distributions
            (np.array([1.0, 0.0]), np.array([0.0, 1.0]), 0.0),  # Completely different
            (
                np.array([0.5, 0.5]),
                np.array([0.0, 1.0]),
                0.7071067811865475,
            ),  # Partially different
            (
                np.array([0.3, 0.7]),
                np.array([0.7, 0.3]),
                0.86,
            ),  # Partially different (approx value)
        ],
    )
    def test_similarity_calculation(self, hellingeraffinitysimilarity, x, y, expected):
        """Test similarity calculation with different probability distributions."""
        similarity = hellingeraffinitysimilarity.similarity(x, y)
        assert np.isclose(similarity, expected, rtol=1e-2)

    def test_different_dimensions(self, hellingeraffinitysimilarity):
        """Test similarity with vectors of different dimensions."""
        x = np.array([0.5, 0.5])
        y = np.array([0.3, 0.3, 0.4])
        with pytest.raises(
            ValueError, match="Probability vectors must have the same shape"
        ):
            hellingeraffinitysimilarity.similarity(x, y)


@pytest.mark.unit
class TestSimilarities:
    """Tests for the similarities calculation."""

    def test_multiple_similarities(self, hellingeraffinitysimilarity):
        """Test calculating similarities against multiple distributions."""
        x = np.array([0.5, 0.5])
        ys = [
            np.array([0.5, 0.5]),  # Same as x
            np.array([0.0, 1.0]),  # Different from x
            np.array([0.3, 0.7]),  # Partially different
        ]
        expected = [1.0, 0.7071067811865475, 0.9486832980505138]

        similarities = hellingeraffinitysimilarity.similarities(x, ys)

        assert len(similarities) == len(ys)
        for sim, exp in zip(similarities, expected):
            assert np.isclose(sim, exp, rtol=1e-10)

    def test_empty_list(self, hellingeraffinitysimilarity):
        """Test similarities with an empty list."""
        x = np.array([0.5, 0.5])
        ys = []

        similarities = hellingeraffinitysimilarity.similarities(x, ys)

        assert similarities == []


@pytest.mark.unit
class TestDissimilarity:
    """Tests for the dissimilarity calculation."""

    @pytest.mark.parametrize(
        "x, y, expected",
        [
            (np.array([1.0, 0.0]), np.array([1.0, 0.0]), 0.0),  # Same distributions
            (np.array([0.5, 0.5]), np.array([0.5, 0.5]), 0.0),  # Same distributions
            (np.array([1.0, 0.0]), np.array([0.0, 1.0]), 1.0),  # Completely different
            (
                np.array([0.5, 0.5]),
                np.array([0.0, 1.0]),
                0.2928932188134525,
            ),  # Partially different
        ],
    )
    def test_dissimilarity_calculation(
        self, hellingeraffinitysimilarity, x, y, expected
    ):
        """Test dissimilarity calculation with different probability distributions."""
        dissimilarity = hellingeraffinitysimilarity.dissimilarity(x, y)
        assert np.isclose(dissimilarity, expected, rtol=1e-10)


@pytest.mark.unit
class TestDissimilarities:
    """Tests for the dissimilarities calculation."""

    def test_multiple_dissimilarities(self, hellingeraffinitysimilarity):
        """Test calculating dissimilarities against multiple distributions."""
        x = np.array([0.5, 0.5])
        ys = [
            np.array([0.5, 0.5]),  # Same as x
            np.array([0.0, 1.0]),  # Different from x
            np.array([0.3, 0.7]),  # Partially different
        ]
        expected = [0.0, 0.2928932188134525, 0.05131670194948623]

        dissimilarities = hellingeraffinitysimilarity.dissimilarities(x, ys)

        assert len(dissimilarities) == len(ys)
        for dissim, exp in zip(dissimilarities, expected):
            assert np.isclose(dissim, exp, rtol=1e-10)


@pytest.mark.unit
class TestProperties:
    """Tests for the similarity properties."""

    def test_bounded(self, hellingeraffinitysimilarity):
        """Test that the similarity measure is bounded."""
        assert hellingeraffinitysimilarity.check_bounded() is True

    def test_reflexivity(self, hellingeraffinitysimilarity):
        """Test the reflexivity property."""
        x = np.array([0.3, 0.7])
        assert hellingeraffinitysimilarity.check_reflexivity(x) is True

    def test_symmetry(self, hellingeraffinitysimilarity):
        """Test the symmetry property."""
        x = np.array([0.3, 0.7])
        y = np.array([0.7, 0.3])
        assert hellingeraffinitysimilarity.check_symmetry(x, y) is True

    def test_identity_of_discernibles_true(self, hellingeraffinitysimilarity):
        """Test the identity of discernibles property when distributions are equal."""
        x = np.array([0.3, 0.7])
        y = np.array([0.3, 0.7])
        assert hellingeraffinitysimilarity.check_identity_of_discernibles(x, y) is True

    def test_identity_of_discernibles_false(self, hellingeraffinitysimilarity):
        """Test the identity of discernibles property when distributions are different."""
        x = np.array([0.3, 0.7])
        y = np.array([0.7, 0.3])
        assert hellingeraffinitysimilarity.check_identity_of_discernibles(x, y) is True


@pytest.mark.unit
class TestEdgeCases:
    """Tests for edge cases."""

    def test_degenerate_distributions(self, hellingeraffinitysimilarity):
        """Test with degenerate distributions (all mass at one point)."""
        x = np.array([1.0, 0.0, 0.0])
        y = np.array([0.0, 1.0, 0.0])
        z = np.array([0.0, 0.0, 1.0])

        # All should be 0 as distributions have no overlap
        assert hellingeraffinitysimilarity.similarity(x, y) == 0.0
        assert hellingeraffinitysimilarity.similarity(x, z) == 0.0
        assert hellingeraffinitysimilarity.similarity(y, z) == 0.0

    def test_uniform_distributions(self, hellingeraffinitysimilarity):
        """Test with uniform distributions."""
        x = np.array([0.25, 0.25, 0.25, 0.25])
        y = np.array([0.25, 0.25, 0.25, 0.25])

        # Should be 1.0 as distributions are identical
        assert hellingeraffinitysimilarity.similarity(x, y) == 1.0


@pytest.mark.unit
def test_serialization(hellingeraffinitysimilarity):
    """Test serialization and deserialization."""
    # Serialize to JSON
    json_str = hellingeraffinitysimilarity.model_dump_json()

    # Deserialize from JSON
    deserialized = HellingerAffinitySimilarity.model_validate_json(json_str)

    # Check type
    assert isinstance(deserialized, HellingerAffinitySimilarity)
    assert deserialized.type == "HellingerAffinitySimilarity"
