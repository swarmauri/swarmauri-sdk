import pytest
import numpy as np
from swarmauri_standard.swarmauri_standard.similarities.CosineSimilarity import CosineSimilarity

@pytest.mark.unit
class TestCosineSimilarity:

    def test_similarity_valid_input(self):
        """Tests the cosine similarity calculation with valid input vectors."""
        a = np.array([1, 2, 3])
        b = np.array([4, 5, 6])
        cosine_sim = CosineSimilarity()
        result = cosine_sim.similarity(a, b)
        assert isinstance(result, float)
        assert result >= -1.0 and result <= 1.0

    def test_similarity_zero_vectors(self):
        """Tests the cosine similarity with zero vectors."""
        a = np.array([0, 0, 0])
        b = np.array([1, 2, 3])
        cosine_sim = CosineSimilarity()
        with pytest.raises(ValueError):
            cosine_sim.similarity(a, b)

    def test_similarity_none_input(self):
        """Tests the cosine similarity with None input vectors."""
        a = None
        b = np.array([1, 2, 3])
        cosine_sim = CosineSimilarity()
        with pytest.raises(ValueError):
            cosine_sim.similarity(a, b)

    def test_similarities_valid_input(self):
        """Tests the similarities method with valid input vectors."""
        a = np.array([1, 2, 3])
        b_list = [np.array([4, 5, 6]), np.array([7, 8, 9])]
        cosine_sim = CosineSimilarity()
        results = cosine_sim.similarities(a, b_list)
        assert isinstance(results, tuple)
        assert len(results) == len(b_list)

    def test_similarities_empty_list(self):
        """Tests the similarities method with an empty list."""
        a = np.array([1, 2, 3])
        b_list = []
        cosine_sim = CosineSimilarity()
        with pytest.raises(ValueError):
            cosine_sim.similarities(a, b_list)

    def test_dissimilarity_valid_input(self):
        """Tests the dissimilarity calculation with valid input vectors."""
        a = np.array([1, 2, 3])
        b = np.array([4, 5, 6])
        cosine_sim = CosineSimilarity()
        sim = cosine_sim.similarity(a, b)
        dissim = cosine_sim.dissimilarity(a, b)
        assert dissim == 1.0 - sim

    def test_dissimilarities_valid_input(self):
        """Tests the dissimilarities method with valid input vectors."""
        a = np.array([1, 2, 3])
        b_list = [np.array([4, 5, 6]), np.array([7, 8, 9])]
        cosine_sim = CosineSimilarity()
        sims = cosine_sim.similarities(a, b_list)
        dissims = cosine_sim.dissimilarities(a, b_list)
        assert isinstance(dissims, tuple)
        assert len(dissims) == len(b_list)
        for d, s in zip(dissims, sims):
            assert d == 1.0 - s

    def test_check_boundedness(self):
        """Tests the boundedness check."""
        cosine_sim = CosineSimilarity()
        a = np.array([1, 2, 3])
        b = np.array([4, 5, 6])
        assert cosine_sim.check_boundedness(a, b) is True

    def test_check_reflexivity_valid(self):
        """Tests the reflexivity check with valid input."""
        a = np.array([1, 2, 3])
        cosine_sim = CosineSimilarity()
        assert cosine_sim.check_reflexivity(a) is True

    def test_check_reflexivity_zero_vector(self):
        """Tests the reflexivity check with zero vector."""
        a = np.array([0, 0, 0])
        cosine_sim = CosineSimilarity()
        assert cosine_sim.check_reflexivity(a) is False

    def test_check_symmetry(self):
        """Tests the symmetry check."""
        a = np.array([1, 2, 3])
        b = np.array([4, 5, 6])
        cosine_sim = CosineSimilarity()
        assert cosine_sim.check_symmetry(a, b) is True

    def test_check_identity_same_vectors(self):
        """Tests the identity check with identical vectors."""
        a = np.array([1, 2, 3])
        b = np.array([1, 2, 3])
        cosine_sim = CosineSimilarity()
        assert cosine_sim.check_identity(a, b) is True

    def test_check_identity_different_vectors(self):
        """Tests the identity check with different vectors."""
        a = np.array([1, 2, 3])
        b = np.array([4, 5, 6])
        cosine_sim = CosineSimilarity()
        assert cosine_sim.check_identity(a, b) is False

    def test_type_property(self):
        """Tests the type property."""
        cosine_sim = CosineSimilarity()
        assert cosine_sim.type == "CosineSimilarity"

    def test_resource_property(self):
        """Tests the resource property."""
        cosine_sim = CosineSimilarity()
        assert cosine_sim.resource == "Similarity"