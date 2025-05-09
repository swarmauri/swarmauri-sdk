import pytest
from swarmauri_standard.similarities.DiceSimilarity import DiceSimilarity
from typing import Union, Sequence, Tuple
import logging
from unittest.mock import patch

logger = logging.getLogger(__name__)


@pytest.mark.unit
class TestDiceSimilarity:
    """
    Unit tests for the DiceSimilarity class.

    This test suite validates the implementation of the DiceSimilarity class,
    ensuring it behaves as expected for various input scenarios.
    """

    @pytest.mark.parametrize(
        "x,y,expected_similarity",
        [
            ("abc", "abc", 1.0),
            ("abc", "def", 0.0),
            ("abcc", "abbc", 0.8),
            ("a", "a", 1.0),
            ("a", "b", 0.0),
            ("", "", 1.0),
            ("", "a", 0.0),
        ],
    )
    def test_similarity(self, x: str, y: str, expected_similarity: float) -> None:
        """
        Test the similarity method with various string inputs.

        Args:
            x: First string to compare
            y: Second string to compare
            expected_similarity: Expected similarity score
        """
        dice = DiceSimilarity()
        similarity = dice.similarity(x, y)
        assert abs(similarity - expected_similarity) < 1e-6

    @pytest.mark.parametrize(
        "x,y,expected_similarity",
        [
            (["a", "b", "c"], ["a", "b", "c"], 1.0),
            (["a", "b", "c"], ["d", "e", "f"], 0.0),
            (["a", "a", "b"], ["a", "b", "b"], 0.8),
            (["a"], ["a"], 1.0),
            (["a"], ["b"], 0.0),
            (["a", "a", "a"], ["a", "a", "a"], 1.0),
        ],
    )
    def test_similarity_list_input(
        self, x: Sequence, y: Sequence, expected_similarity: float
    ) -> None:
        """
        Test the similarity method with list inputs.

        Args:
            x: First list to compare
            y: Second list to compare
            expected_similarity: Expected similarity score
        """
        dice = DiceSimilarity()
        similarity = dice.similarity(x, y)
        assert abs(similarity - expected_similarity) < 1e-6

    def test_similarities_batch_mode(self) -> None:
        """
        Test the similarities method with batch inputs.
        """
        dice = DiceSimilarity()
        xs = ["a", "b", "c"]
        ys = ["a", "b", "c"]
        similarities = dice.similarities(xs, ys)
        assert len(similarities) == 3
        assert all(s == 1.0 for s in similarities)

    def test_similarities_single_pair(self) -> None:
        """
        Test the similarities method with single pair input.
        """
        dice = DiceSimilarity()
        similarity = dice.similarities("a", "a")
        assert similarity == 1.0

    @pytest.mark.parametrize(
        "x,y,expected_dissimilarity",
        [
            ("a", "a", 0.0),
            ("a", "b", 1.0),
            ("ab", "cd", 1.0),
            ("ab", "ab", 0.0),
        ],
    )
    def test_dissimilarity(self, x: str, y: str, expected_dissimilarity: float) -> None:
        """
        Test the dissimilarity method.

        Args:
            x: First input to compare
            y: Second input to compare
            expected_dissimilarity: Expected dissimilarity score
        """
        dice = DiceSimilarity()
        dissimilarity = dice.dissimilarity(x, y)
        assert abs(dissimilarity - expected_dissimilarity) < 1e-6

    def test_dissimilarities_batch_mode(self) -> None:
        """
        Test the dissimilarities method with batch inputs.
        """
        dice = DiceSimilarity()
        xs = ["a", "b", "c"]
        ys = ["a", "b", "c"]
        dissimilarities = dice.dissimilarities(xs, ys)
        assert len(dissimilarities) == 3
        assert all(d == 0.0 for d in dissimilarities)

    def test_check_boundedness(self) -> None:
        """
        Test the check_boundedness method.
        """
        dice = DiceSimilarity()
        assert dice.check_boundedness() is True

    def test_check_reflexivity(self) -> None:
        """
        Test the check_reflexivity method.
        """
        dice = DiceSimilarity()
        assert dice.check_reflexivity() is True

    def test_check_symmetry(self) -> None:
        """
        Test the check_symmetry method.
        """
        dice = DiceSimilarity()
        assert dice.check_symmetry() is True

    @patch_logger
    def test_logging_similarity(self, mock_logger: Callable) -> None:
        """
        Test that logging is correctly implemented in similarity method.

        Args:
            mock_logger: Mocked logger instance
        """
        dice = DiceSimilarity()
        dice.similarity("a", "b")
        mock_logger.debug.assert_called_once_with(
            "Calculating Dice similarity between a and b"
        )

    @patch_logger
    def test_logging_dissimilarity(self, mock_logger: Callable) -> None:
        """
        Test that logging is correctly implemented in dissimilarity method.

        Args:
            mock_logger: Mocked logger instance
        """
        dice = DiceSimilarity()
        dice.dissimilarity("a", "b")
        mock_logger.debug.assert_called_once_with(
            "Calculating dissimilarity between a and b"
        )
