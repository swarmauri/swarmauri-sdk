import pytest
import logging
from swarmauri_standard.similarities.DiceSimilarity import DiceSimilarity

@pytest.mark.unit
class TestDiceSimilarity:
    """Unit tests for the DiceSimilarity class."""
    
    @pytest.fixture
    def dice_similarity(self):
        """Fixture to provide a DiceSimilarity instance."""
        return DiceSimilarity()

    @pytest.fixture
    def logger(self, caplog):
        """Fixture to capture logging output."""
        return caplog

    @pytest.mark.parametrize("x,y,expected", [
        ("abc", "abc", 1.0),
        ("abc", "abd", 2/3),
        ("ab", "ba", 1.0),
        ("a", "b", 0.0),
        ("", "", 0.0),
        ([], [], 0.0),
        ([1, 2, 3], [1, 2, 3], 1.0),
        ([1, 2, 3], [1, 2, 4], (2/3)/2)  # Edge case where size_x + size_y is small
    ])
    def test_similarity(self, x, y, expected, dice_similarity):
        """Test the similarity method with various inputs."""
        result = dice_similarity.similarity(x, y)
        assert result == pytest.approx(expected)

    @pytest.mark.parametrize("x,y,expected", [
        ("a", "a", True),
        ("a", "b", False),
        ("ab", "ab", True),
        ("ab", "ba", True),
        ("a", "", False)
    ])
    def test_check_identity(self, x, y, expected, dice_similarity):
        """Test the check_identity method."""
        result = dice_similarity.check_identity(x, y)
        assert result == expected

    @pytest.mark.parametrize("x,expected", [
        ("test", True),
        (set(), True),
        ("", True),
        (123, True)
    ])
    def test_check_reflexivity(self, x, expected, dice_similarity):
        """Test the check_reflexivity method."""
        result = dice_similarity.check_reflexivity(x)
        assert result == expected

    @pytest.mark.parametrize("x,y,expected", [
        ("a", "a", True),
        ("a", "b", False),
        ("ab", "ba", True),
        ("ab", "cd", False),
        ([1, 2], [2, 1], True)
    ])
    def test_check_symmetry(self, x, y, expected, dice_similarity):
        """Test the check_symmetry method."""
        result = dice_similarity.check_symmetry(x, y)
        assert result == expected

    @pytest.mark.parametrize("x,y,expected", [
        ("a", "b", True),
        ("ab", "cd", True),
        ("", "", True),
        ([1], [2], True)
    ])
    def test_check_boundedness(self, x, y, expected, dice_similarity):
        """Test the check_boundedness method."""
        result = dice_similarity.check_boundedness(x, y)
        assert result == expected

    def test_serialization(self, dice_similarity):
        """Test model serialization and validation."""
        model_json = dice_similarity.model_dump_json()
        model_id = dice_similarity.id
        assert model_id == dice_similarity.model_validate_json(model_json)

    def test_dissimilarity(self, dice_similarity):
        """Test the dissimilarity method."""
        similarity = dice_similarity.similarity("a", "b")
        dissimilarity = dice_similarity.dissimilarity("a", "b")
        assert dissimilarity == 1.0 - similarity

    def test_similarities_with_multiple_inputs(self, dice_similarity):
        """Test the similarities method with multiple inputs."""
        x = "test"
        ys = ["test", "ttest", "testing", "test"]
        results = dice_similarity.similarities(x, ys)
        assert isinstance(results, list)
        assert len(results) == len(ys)

    def test_similarities_with_single_input(self, dice_similarity):
        """Test the similarities method with a single input."""
        x = "test"
        y = "test"
        result = dice_similarity.similarities(x, y)
        assert isinstance(result, float)

    def test_dissimilarities(self, dice_similarity):
        """Test the dissimilarities method."""
        x = "a"
        ys = ["a", "b", "ab"]
        similarities = dice_similarity.similarities(x, ys)
        if isinstance(similarities, float):
            dissimilarities = dice_similarity.dissimilarities(x, ys)
            assert isinstance(dissimilarities, float)
            assert dissimilarities == 1.0 - similarities
        else:
            dissimilarities = dice_similarity.dissimilarities(x, ys)
            assert isinstance(dissimilarities, list)
            assert len(dissimilarities) == len(ys))

    def test_invalid_input_handling(self, dice_similarity):
        """Test handling of invalid inputs."""
        with pytest.raises(ValueError):
            dice_similarity.similarity(None, "test")
        with pytest.raises(ValueError):
            dice_similarity.similarity("test", None)
        with pytest.raises(ValueError):
            dice_similarity.similarity(123, "test")  # Assuming 123 is not iterable