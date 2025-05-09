import pytest
from swarmauri_standard.similarities.JaccardIndexSimilarity import JaccardIndexSimilarity
import logging

@pytest.mark.unit
class TestJaccardIndexSimilarity:
    """Unit tests for JaccardIndexSimilarity class."""
    
    def test_similarity_identical_sets(self):
        """Test similarity calculation for identical sets."""
        jaccard = JaccardIndexSimilarity()
        set1 = {1, 2, 3}
        set2 = {1, 2, 3}
        assert jaccard.similarity(set1, set2) == 1.0
        logging.debug("Test identical sets passed")

    def test_similarity_disjoint_sets(self):
        """Test similarity calculation for disjoint sets."""
        jaccard = JaccardIndexSimilarity()
        set1 = {1, 2, 3}
        set2 = {4, 5, 6}
        assert jaccard.similarity(set1, set2) == 0.0
        logging.debug("Test disjoint sets passed")

    def test_similarity_partial_overlap(self):
        """Test similarity calculation for sets with partial overlap."""
        jaccard = JaccardIndexSimilarity()
        set1 = {1, 2, 3}
        set2 = {3, 4, 5}
        assert jaccard.similarity(set1, set2) == 1/5  # |{3}| / |{1,2,3,4,5}|
        logging.debug("Test partial overlap sets passed")

    def test_similarity_invalid_input(self):
        """Test similarity with invalid input types."""
        jaccard = JaccardIndexSimilarity()
        with pytest.raises(ValueError):
            jaccard.similarity([1,2], {1,2})
        logging.debug("Test invalid input types passed")

    def test_dissimilarity_identical_sets(self):
        """Test dissimilarity calculation for identical sets."""
        jaccard = JaccardIndexSimilarity()
        set1 = {1, 2, 3}
        set2 = {1, 2, 3}
        assert jaccard.dissimilarity(set1, set2) == 0.0
        logging.debug("Test identical sets dissimilarity passed")

    def test_dissimilarity_disjoint_sets(self):
        """Test dissimilarity calculation for disjoint sets."""
        jaccard = JaccardIndexSimilarity()
        set1 = {1, 2, 3}
        set2 = {4, 5, 6}
        assert jaccard.dissimilarity(set1, set2) == 1.0
        logging.debug("Test disjoint sets dissimilarity passed")

    def test_dissimilarity_partial_overlap(self):
        """Test dissimilarity calculation for sets with partial overlap."""
        jaccard = JaccardIndexSimilarity()
        set1 = {1, 2, 3}
        set2 = {3, 4, 5}
        assert jaccard.dissimilarity(set1, set2) == 4/5  # 1 - (1/5)
        logging.debug("Test partial overlap dissimilarity passed")

    def test_similarities_multiple_pairs(self):
        """Test similarities calculation for multiple pairs."""
        jaccard = JaccardIndexSimilarity()
        pairs = [
            ({1, 2}, {1, 2, 3}),
            ({1, 2, 3}, {3, 4, 5}),
            ({}, {1})
        ]
        expected = [2/3, 1/5, 0.0]
        assert jaccard.similarities(pairs) == expected
        logging.debug("Test multiple pairs similarities passed")

    def test_dissimilarities_multiple_pairs(self):
        """Test dissimilarities calculation for multiple pairs."""
        jaccard = JaccardIndexSimilarity()
        pairs = [
            ({1, 2}, {1, 2, 3}),
            ({1, 2, 3}, {3, 4, 5}),
            ({}, {1})
        ]
        expected = [1/3, 4/5, 1.0]
        assert jaccard.dissimilarities(pairs) == expected
        logging.debug("Test multiple pairs dissimilarities passed")

    def test_type_property(self):
        """Test the type property."""
        assert JaccardIndexSimilarity.type == "JaccardIndexSimilarity"
        logging.debug("Test type property passed")

    def test_resource_property(self):
        """Test the resource property."""
        assert JaccardIndexSimilarity.resource == "Similarity"
        logging.debug("Test resource property passed"

    def test_edge_cases(self):
        """Test edge cases including empty sets."""
        jaccard = JaccardIndexSimilarity()
        
        # Both sets empty
        set1 = set()
        set2 = set()
        assert jaccard.similarity(set1, set2) == 1.0
        assert jaccard.dissimilarity(set1, set2) == 0.0
        
        # One set empty
        set3 = {1, 2, 3}
        assert jaccard.similarity(set1, set3) == 0.0
        assert jaccard.dissimilarity(set1, set3) == 1.0
        logging.debug("Test edge cases passed")