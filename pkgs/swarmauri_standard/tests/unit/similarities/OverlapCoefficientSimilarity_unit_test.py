import pytest
import logging
from swarmauri_standard.swarmauri_standard.similarities.OverlapCoefficientSimilarity import (
    OverlapCoefficientSimilarity,
)


@pytest.mark.unit
class TestOverlapCoefficientSimilarity:
    """Unit tests for the OverlapCoefficientSimilarity class."""

    @pytest.fixture
    def overlap_coefficient(self):
        """Fixture to create an instance of OverlapCoefficientSimilarity."""
        return OverlapCoefficientSimilarity()

    @pytest.mark.unit
    def test_initialization(self, overlap_coefficient, caplog):
        """Test that the OverlapCoefficientSimilarity instance is initialized correctly."""
        assert isinstance(overlap_coefficient, OverlapCoefficientSimilarity)
        assert hasattr(overlap_coefficient, "_logger")
        assert isinstance(overlap_coefficient._logger, logging.Logger)
        with caplog.at_level(logging.DEBUG):
            overlap_coefficient.similarity({"a", "b"}, {"a", "b", "c"})
            assert "Overlap Coefficient Similarity" in caplog.text

    @pytest.mark.unit
    def test_similarity(self, overlap_coefficient):
        """Test the similarity calculation with various inputs."""
        # Test with strings
        assert overlap_coefficient.similarity("test", "test") == 1.0
        # Test with lists
        assert (
            overlap_coefficient.similarity(["a", "b"], ["a", "b", "c"]) == 2 / 2 == 1.0
        )
        # Test with sets
        assert (
            overlap_coefficient.similarity({"a", "b", "c"}, {"a", "b"}) == 2 / 2 == 1.0
        )
        # Test with empty set
        with pytest.raises(ValueError):
            overlap_coefficient.similarity("", "test")

    @pytest.mark.unit
    def test_serialization(self, overlap_coefficient):
        """Test the model serialization methods."""
        model_json = overlap_coefficient.model_dump_json()
        loaded_json = overlap_coefficient.model_validate_json(model_json)
        assert model_json == loaded_json

    @pytest.mark.unit
    def test_similarities_multiple(self, overlap_coefficient):
        """Test the similarities method with multiple inputs."""
        single_similarity = overlap_coefficient.similarity({"a"}, {"a"})
        multiple_similarity = overlap_coefficient.similarities(
            {"a"}, [{"a"}, {"a", "b"}]
        )
        assert isinstance(multiple_similarity, list)
        assert single_similarity in multiple_similarity

    @pytest.mark.unit
    def test_edge_cases(self, overlap_coefficient):
        """Test edge cases for similarity calculation."""
        with pytest.raises(ValueError):
            overlap_coefficient.similarity("", "")
        assert overlap_coefficient.similarity("a", "a") == 1.0
        assert overlap_coefficient.similarity("a", "b") == 0.0

    @pytest.mark.unit
    def test_dissimilarity(self, overlap_coefficient):
        """Test the dissimilarity calculation."""
        similarity = overlap_coefficient.similarity({"a"}, {"a", "b"})
        dissimilarity = overlap_coefficient.dissimilarity({"a"}, {"a", "b"})
        assert dissimilarity == 1 - similarity

    @pytest.mark.unit
    def test_check_boundedness(self, overlap_coefficient):
        """Test the boundedness check."""
        assert overlap_coefficient.check_boundedness({"a"}, {"a"})

    @pytest.mark.unit
    def test_check_reflexivity(self, overlap_coefficient):
        """Test the reflexivity check."""
        assert overlap_coefficient.check_reflexivity({"a"})

    @pytest.mark.unit
    def test_check_symmetry(self, overlap_coefficient):
        """Test the symmetry check."""
        assert overlap_coefficient.check_symmetry({"a"}, {"a"})

    @pytest.mark.unit
    def test_check_identity(self, overlap_coefficient):
        """Test the identity check."""
        assert overlap_coefficient.check_identity({"a"}, {"a"})
        assert not overlap_coefficient.check_identity({"a"}, {"b"})

    @pytest.mark.unit
    def test_similarity_parameterization(self, overlap_coefficient):
        """Test similarity calculation with different input types."""
        test_cases = [
            ({"a"}, {"a"}, 1.0),
            ({"a", "b"}, {"a", "b", "c"}, 2 / 2),
            (["a", "b"], ["a", "b", "c"], 2 / 2),
            ("a", "a", 1.0),
            ("a", "b", 0.0),
            ({"a", "b", "c"}, {"a", "b", "d"}, 2 / 3),
        ]

        for x, y, expected in test_cases:
            assert overlap_coefficient.similarity(x, y) == expected
