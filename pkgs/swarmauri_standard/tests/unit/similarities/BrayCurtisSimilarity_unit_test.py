import pytest
from swarmauri_standard.swarmauri_standard.similarities.BrayCurtisSimilarity import (
    BrayCurtisSimilarity,
)
import logging


@pytest.mark.unit
class TestBrayCurtisSimilarity:
    @pytest.fixture
    def braycurtis_instance(self):
        """Fixture to create an instance of BrayCurtisSimilarity."""
        return BrayCurtisSimilarity()

    @pytest.mark.unit
    def test_similarity_with_identical_vectors(self, braycurtis_instance):
        """Test similarity with identical vectors."""
        x = (1, 2, 3)
        y = (1, 2, 3)
        result = braycurtis_instance.similarity(x, y)
        assert result == 1.0

    @pytest.mark.unit
    def test_similarity_with_different_vectors(self, braycurtis_instance):
        """Test similarity with different vectors."""
        x = (1, 2, 3)
        y = (4, 5, 6)
        result = braycurtis_instance.similarity(x, y)
        assert result < 1.0

    @pytest.mark.unit
    def test_similarity_with_empty_vectors(self, braycurtis_instance):
        """Test similarity with empty vectors."""
        x = ()
        y = ()
        result = braycurtis_instance.similarity(x, y)
        assert result == 1.0

    @pytest.mark.unit
    def test_similarity_with_negative_values(self, braycurtis_instance):
        """Test similarity with negative values."""
        x = (1, -2, 3)
        y = (4, 5, 6)
        with pytest.raises(ValueError):
            braycurtis_instance.similarity(x, y)

    @pytest.mark.unit
    def test_similarities_with_multiple_vectors(self, braycurtis_instance):
        """Test similarities with multiple vectors."""
        x = (1, 2, 3)
        ys = [(4, 5, 6), (7, 8, 9)]
        results = braycurtis_instance.similarities(x, ys)
        assert len(results) == 2

    @pytest.mark.unit
    def test_dissimilarity(self, braycurtis_instance):
        """Test dissimilarity calculation."""
        x = (1, 2, 3)
        y = (4, 5, 6)
        similarity = braycurtis_instance.similarity(x, y)
        dissimilarity = braycurtis_instance.dissimilarity(x, y)
        assert dissimilarity == 1 - similarity

    @pytest.mark.unit
    def test_check_boundedness(self, braycurtis_instance):
        """Test boundedness check."""
        x = (1, 2, 3)
        y = (4, 5, 6)
        result = braycurtis_instance.check_boundedness(x, y)
        assert result is True

    @pytest.mark.unit
    def test_check_reflexivity(self, braycurtis_instance):
        """Test reflexivity check."""
        x = (1, 2, 3)
        result = braycurtis_instance.check_reflexivity(x)
        assert result is True

    @pytest.mark.unit
    def test_check_symmetry(self, braycurtis_instance):
        """Test symmetry check."""
        x = (1, 2, 3)
        y = (4, 5, 6)
        result = braycurtis_instance.check_symmetry(x, y)
        assert result is True

    @pytest.mark.unit
    def test_check_identity(self, braycurtis_instance):
        """Test identity check."""
        x = (1, 2, 3)
        y = (1, 2, 3)
        result = braycurtis_instance.check_identity(x, y)
        assert result is True

    @pytest.mark.unit
    def test_check_identity_with_different_vectors(self, braycurtis_instance):
        """Test identity check with different vectors."""
        x = (1, 2, 3)
        y = (4, 5, 6)
        result = braycurtis_instance.check_identity(x, y)
        assert result is False

    @pytest.mark.unit
    def test_logging(self, braycurtis_instance, caplog):
        """Test logging in similarity method."""
        x = (1, 2, 3)
        y = (4, 5, 6)
        with caplog.at_level(logging.DEBUG):
            braycurtis_instance.similarity(x, y)
            assert "Bray-Curtis similarity calculated" in caplog.text
