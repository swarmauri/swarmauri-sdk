import pytest
import unittest
from swarmauri_standard.swarmauri_standard.similarities.TanimotoSimilarity import TanimotoSimilarity
import logging

logger = logging.getLogger(__name__)


@pytest.mark.unit
class TestTanimotoSimilarity(unittest.TestCase):
    """
    Unit tests for the TanimotoSimilarity class.

    This test class provides comprehensive unit tests for the TanimotoSimilarity
    class implementation. It tests all public methods and their expected behavior,
    including edge cases and error handling.
    """

    def setUp(self):
        """
        Set up the test fixture.

        Initialize the TanimotoSimilarity instance before each test case.
        """
        self.tanimoto = TanimotoSimilarity()

    def test_similarity_with_valid_vectors(self):
        """
        Test the similarity method with valid vectors.

        Verify that the Tanimoto similarity is correctly calculated for non-empty vectors.
        """
        a = [1, 2, 3]
        b = [4, 5, 6]
        result = self.tanimoto.similarity(a, b)
        self.assertIsInstance(result, float)
        self.assertGreaterEqual(result, 0.0)
        self.assertLessEqual(result, 1.0)

    def test_similarity_with_identical_vectors(self):
        """
        Test the similarity method with identical vectors.

        Verify that the similarity of a vector with itself returns 1.0.
        """
        a = [1, 2, 3]
        result = self.tanimoto.similarity(a, a)
        self.assertEqual(result, 1.0)

    def test_similarity_with_zero_vector(self):
        """
        Test the similarity method with a zero vector.

        Verify that the similarity calculation handles zero vectors correctly.
        """
        a = [0, 0, 0]
        b = [1, 2, 3]
        with self.assertRaises(ValueError):
            self.tanimoto.similarity(a, b)

    def test_similarity_with_none_vectors(self):
        """
        Test the similarity method with None vectors.

        Verify that the method raises a ValueError when either vector is None.
        """
        a = None
        b = [1, 2, 3]
        with self.assertRaises(ValueError):
            self.tanimoto.similarity(a, b)

    def test_similarities_with_valid_vectors(self):
        """
        Test the similarities method with valid vectors.

        Verify that the method correctly calculates similarities for a list of vectors.
        """
        a = [1, 2, 3]
        b_list = [[4, 5, 6], [7, 8, 9]]
        results = self.tanimoto.similarities(a, b_list)
        self.assertIsInstance(results, tuple)
        self.assertEqual(len(results), len(b_list))

    def test_similarities_with_empty_list(self):
        """
        Test the similarities method with an empty list.

        Verify that the method returns an empty tuple when the input list is empty.
        """
        a = [1, 2, 3]
        b_list = []
        results = self.tanimoto.similarities(a, b_list)
        self.assertEqual(results, tuple())

    def test_dissimilarity_with_valid_vectors(self):
        """
        Test the dissimilarity method with valid vectors.

        Verify that the dissimilarity is calculated as 1 - similarity.
        """
        a = [1, 2, 3]
        b = [4, 5, 6]
        similarity = self.tanimoto.similarity(a, b)
        dissimilarity = self.tanimoto.dissimilarity(a, b)
        self.assertEqual(dissimilarity, 1.0 - similarity)

    def test_dissimilarities_with_valid_vectors(self):
        """
        Test the dissimilarities method with valid vectors.

        Verify that the method correctly calculates dissimilarities for a list of vectors.
        """
        a = [1, 2, 3]
        b_list = [[4, 5, 6], [7, 8, 9]]
        similarities = self.tanimoto.similarities(a, b_list)
        dissimilarities = self.tanimoto.dissimilarities(a, b_list)
        self.assertEqual(len(dissimilarities), len(similarities))
        for d, s in zip(dissimilarities, similarities):
            self.assertEqual(d, 1.0 - s)

    def test_check_boundedness(self):
        """
        Test the check_boundedness method.

        Verify that the method returns True, as Tanimoto similarity is bounded between 0 and 1.
        """
        a = [1, 2, 3]
        b = [4, 5, 6]
        result = self.tanimoto.check_boundedness(a, b)
        self.assertTrue(result)

    def test_check_reflexivity(self):
        """
        Test the check_reflexivity method.

        Verify that the similarity of a vector with itself returns 1.0.
        """
        a = [1, 2, 3]
        result = self.tanimoto.check_reflexivity(a)
        self.assertTrue(result)

    def test_check_symmetry(self):
        """
        Test the check_symmetry method.

        Verify that the similarity is symmetric, i.e., s(a, b) = s(b, a).
        """
        a = [1, 2, 3]
        b = [4, 5, 6]
        s_ab = self.tanimoto.similarity(a, b)
        s_ba = self.tanimoto.similarity(b, a)
        self.assertEqual(s_ab, s_ba)

    def test_check_identity(self):
        """
        Test the check_identity method.

        Verify that the method returns True only when the vectors are identical.
        """
        a = [1, 2, 3]
        b_identical = [1, 2, 3]
        b_different = [4, 5, 6]
        
        # Test with identical vectors
        result_identical = self.tanimoto.check_identity(a, b_identical)
        self.assertTrue(result_identical)
        
        # Test with different vectors
        result_different = self.tanimoto.check_identity(a, b_different)
        self.assertFalse(result_different)

    def test_similarity_with_different_length_vectors(self):
        """
        Test the similarity method with vectors of different lengths.

        Verify that the method raises a ValueError when vector lengths differ.
        """
        a = [1, 2, 3]
        b = [4, 5]
        with self.assertRaises(ValueError):
            self.tanimoto.similarity(a, b)

    def test_similarity_with_all_zero_vectors(self):
        """
        Test the similarity method with all-zero vectors.

        Verify that the method raises a ValueError when both vectors are zero vectors.
        """
        a = [0, 0, 0]
        b = [0, 0, 0]
        with self.assertRaises(ValueError):
            self.tanimoto.similarity(a, b)

    def test_similarities_with_none_in_list(self):
        """
        Test the similarities method with None vectors in the list.

        Verify that the method raises a ValueError when any vector in the list is None.
        """
        a = [1, 2, 3]
        b_list = [None, [4, 5, 6]]
        with self.assertRaises(ValueError):
            self.tanimoto.similarities(a, b_list)