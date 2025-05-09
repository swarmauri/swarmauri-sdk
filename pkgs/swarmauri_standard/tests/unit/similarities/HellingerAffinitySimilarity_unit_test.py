import pytest
import unittest
from unittest.mock import TestCase
import math

from swarmauri_standard.swarmauri_standard.similarities.HellingerAffinitySimilarity import (
    HellingerAffinitySimilarity,
)


@pytest.mark.unit
class TestHellingerAffinitySimilarity(TestCase):
    """Unit tests for the HellingerAffinitySimilarity class."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Fixture to provide a fresh instance of HellingerAffinitySimilarity for each test."""
        self.hellinger_affinity = HellingerAffinitySimilarity()

    def test_init(self):
        """Test that the instance is initialized correctly."""
        assert isinstance(self.hellinger_affinity, HellingerAffinitySimilarity)
        assert self.hellinger_affinity.resource == "Similarity"
        assert self.hellinger_affinity.type == "HellingerAffinitySimilarity"

    @pytest.mark.parametrize(
        "x,y,expected",
        [
            ([1.0, 0.0], [1.0, 0.0], 1.0),  # Identical distributions
            ([0.5, 0.5], [0.5, 0.5], 1.0),  # Identical distributions
            ([1.0, 0.0], [0.0, 1.0], 0.0),  # Completely different
            (
                [0.3, 0.7],
                [0.7, 0.3],
                math.sqrt(0.3 * 0.7) + math.sqrt(0.7 * 0.3),
            ),  # Partial overlap
            ([0.0, 1.0], [0.0, 1.0], 1.0),  # Edge case with zeros
            (
                [0.25, 0.75],
                [0.25, 0.75],
                1.0,
            ),  # Different structure but same distribution
        ],
    )
    def test_similarity(self, x, y, expected):
        """Test the similarity calculation between different probability vectors."""
        result = self.hellinger_affinity.similarity(x, y)
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0
        assert math.isclose(result, expected, rel_tol=1e-9, abs_tol=1e-9)

    @pytest.mark.parametrize(
        "pairs,expected_length",
        [
            ([([1.0, 0.0], [1.0, 0.0]), ([0.5, 0.5], [0.5, 0.5])], 2),
            ([([0.3, 0.7], [0.7, 0.3])], 1),
            ([([1.0, 0.0], [0.0, 1.0])], 1),
        ],
    )
    def test_similarities(self, pairs, expected_length):
        """Test batch similarity calculation."""
        results = self.hellinger_affinity.similarities(pairs)
        assert isinstance(results, list)
        assert len(results) == expected_length
        for result in results:
            assert isinstance(result, float)
            assert 0.0 <= result <= 1.0

    @pytest.mark.parametrize(
        "vector,expected",
        [
            ([1.0, 0.0], True),  # Valid
            ([0.5, 0.5], True),  # Valid
            ([-0.1, 1.1], False),  # Contains negative
            ([0.9, 0.1], True),  # Valid
            ([1.0, 0.0, 0.0], True),  # Valid with zeros
            ([], False),  # Empty vector
            ([2.0], False),  # Sum greater than 1
        ],
    )
    def test_is_valid_probability_vector(self, vector, expected):
        """Test validation of probability vectors."""
        result = self.hellinger_affinity._is_valid_probability_vector(vector)
        assert isinstance(result, bool)
        assert result == expected

    def test_similarity_invalid_vectors(self):
        """Test that invalid vectors raise ValueError."""
        with pytest.raises(ValueError):
            self.hellinger_affinity.similarity([1.0, -0.5], [0.5, 0.5])


if __name__ == "__main__":
    pytest.main([__file__])
