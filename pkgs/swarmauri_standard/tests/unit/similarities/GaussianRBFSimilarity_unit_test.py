import pytest
import numpy as np
import logging

from swarmauri_standard.swarmauri_standard.GaussianRBFSimilarity import GaussianRBFSimilarity

@pytest.mark.unit
class TestGaussianRBFSimilarity:
    """Unit tests for the GaussianRBFSimilarity class."""

    @pytest.mark.parametrize("gamma,expected_valid", [
        (1.0, True),
        (0.5, True),
        (-1.0, False),
        (0.0, False)
    ])
    def test_gamma_validation(self, gamma, expected_valid):
        """Test validation of gamma parameter."""
        if expected_valid:
            GaussianRBFSimilarity(gamma=gamma)
        else:
            with pytest.raises(ValueError):
                GaussianRBFSimilarity(gamma=gamma)

    @pytest.mark.parametrize("a,b,expected_similarity", [
        ([1, 2], [1, 2], 1.0),
        ([1, 2], [2, 3], np.exp(-1.0 * (1.0**2 + 1.0**2))),
        ([0.5, 0.5], [0.5, 0.5], 1.0)
    ])
    def test_similarity(self, a, b, expected_similarity):
        """Test similarity calculation."""
        gsim = GaussianRBFSimilarity()
        similarity = gsim.similarity(a, b)
        assert np.allclose(similarity, expected_similarity, atol=1e-6)

    def test_similarity_invalid_input(self):
        """Test invalid input handling in similarity."""
        gsim = GaussianRBFSimilarity()
        with pytest.raises(ValueError):
            gsim.similarity(None, [1, 2])
        with pytest.raises(ValueError):
            gsim.similarity([1, 2], None)

    @pytest.mark.parametrize("a,b_list,expected_length", [
        ([1, 2], [[2, 3], [3, 4]], 2)
    ])
    def test_similarities(self, a, b_list, expected_length):
        """Test similarities calculation."""
        gsim = GaussianRBFSimilarity()
        similarities = gsim.similarities(a, b_list)
        assert len(similarities) == expected_length
        assert all(0 <= score <= 1 for score in similarities)

    def test_dissimilarity(self):
        """Test dissimilarity calculation."""
        gsim = GaussianRBFSimilarity()
        a = [1, 2]
        b = [1, 2]
        dissim = gsim.dissimilarity(a, b)
        assert np.allclose(dissim, 0.0, atol=1e-6)

        a = [1, 2]
        b = [2, 3]
        dissim = gsim.dissimilarity(a, b)
        assert 0 <= dissim <= 1

    def test_dissimilarities(self):
        """Test dissimilarities calculation."""
        gsim = GaussianRBFSimilarity()
        a = [1, 2]
        b_list = [[2, 3], [3, 4]]
        dissims = gsim.dissimilarities(a, b_list)
        assert len(dissims) == len(b_list)
        assert all(0 <= d <= 1 for d in dissims)

    def test_check_boundedness(self):
        """Test boundedness check."""
        gsim = GaussianRBFSimilarity()
        assert gsim.check_boundedness([1, 2], [1, 2]) is True

    def test_check_reflexivity(self):
        """Test reflexivity check."""
        gsim = GaussianRBFSimilarity()
        assert gsim.check_reflexivity([1, 2]) is True

    def test_check_symmetry(self):
        """Test symmetry check."""
        gsim = GaussianRBFSimilarity()
        assert gsim.check_symmetry([1, 2], [1, 2]) is True

    def test_check_identity(self):
        """Test identity check."""
        gsim = GaussianRBFSimilarity()
        a = [1, 2]
        b = [1, 2]
        assert gsim.check_identity(a, b) is True