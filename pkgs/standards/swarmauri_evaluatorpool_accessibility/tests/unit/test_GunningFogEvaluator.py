import logging
from unittest.mock import MagicMock, patch

import pytest
from swarmauri_core.programs.IProgram import IProgram as Program
from swarmauri_evaluatorpool_accessibility.GunningFogEvaluator import (
    GunningFogEvaluator,
)


@pytest.fixture
def evaluator():
    """
    Fixture providing a GunningFogEvaluator instance for testing.

    Returns:
        GunningFogEvaluator: An instance of the evaluator
    """
    return GunningFogEvaluator()


@pytest.fixture
def mock_program():
    """
    Fixture providing a mock Program for testing.

    Returns:
        MagicMock: A mock program object
    """
    program = MagicMock(spec=Program)
    program.get_source_files.return_value = {"main.txt": ""}
    return program


@pytest.mark.unit
def test_type(evaluator):
    """Test that the evaluator has the correct type identifier."""
    assert evaluator.type == "GunningFogEvaluator"


@pytest.mark.unit
def test_serialization(evaluator):
    """Test that the evaluator can be properly serialized and deserialized."""
    serialized = evaluator.model_dump_json()
    deserialized = GunningFogEvaluator.model_validate_json(serialized)
    assert isinstance(deserialized, GunningFogEvaluator)
    assert deserialized.type == evaluator.type


@pytest.mark.unit
def test_count_sentences(evaluator):
    """Test the sentence counting functionality."""
    text = "This is a sentence. This is another one! Is this a question? Yes, it is."
    assert evaluator._count_sentences(text) == 4

    # Test with empty text
    assert evaluator._count_sentences("") == 0

    # Test with unusual punctuation
    assert evaluator._count_sentences("Hello... World...") == 2


@pytest.mark.unit
def test_count_words(evaluator):
    """Test the word counting functionality."""
    text = "This text has exactly seven words in it."
    assert evaluator._count_words(text) == 8

    # Test with empty text
    assert evaluator._count_words("") == 0

    # Test with punctuation
    assert evaluator._count_words("Hello, world! How's it going?") == 5


@pytest.mark.unit
@pytest.mark.parametrize(
    "word, expected_syllables",
    [
        ("hello", 2),
        ("beautiful", 3),
        ("accessibility", 6),
        ("the", 1),
        ("area", 2),
        ("university", 5),
        ("a", 1),
        ("", 1),  # Edge case, should return minimum 1
    ],
)
def test_count_syllables(evaluator, word, expected_syllables):
    """Test the syllable counting functionality with various words."""
    assert evaluator._count_syllables(word) == expected_syllables


@pytest.mark.unit
def test_count_complex_words(evaluator):
    """Test the complex word counting functionality."""
    text = "The university professor discussed accessibility and utilization of beautiful resources."
    # Complex words: university, professor, accessibility, utilization, beautiful
    assert evaluator._count_complex_words(text) == 5

    # Test with no complex words
    assert evaluator._count_complex_words("The cat sat on the mat.") == 0


@pytest.mark.unit
def test_compute_score_empty_text(evaluator, mock_program):
    """Test compute_score with empty text."""
    mock_program.get_source_files.return_value = {"main.txt": ""}
    score, metadata = evaluator._compute_score(mock_program)

    assert score == 0.0
    assert "error" in metadata
    assert metadata["error"] == "No valid text to analyze"


@pytest.mark.unit
def test_compute_score_invalid_text(evaluator, mock_program):
    """Test compute_score with invalid text type."""
    mock_program.get_source_files.return_value = {"main.txt": None}
    score, metadata = evaluator._compute_score(mock_program)

    assert score == 0.0
    assert "error" in metadata
    assert metadata["error"] == "No valid text to analyze"


@pytest.mark.unit
def test_compute_score_no_sentences(evaluator, mock_program):
    """Test compute_score with text that has no sentences."""
    # Text with words but no sentence terminators
    mock_program.get_source_files.return_value = {
        "main.txt": "words without proper sentence structure"
    }

    # Mock the _count_sentences method to return 0
    with patch.object(evaluator, "_count_sentences", return_value=0):
        score, metadata = evaluator._compute_score(mock_program)

        assert score == 0.0
        assert "error" in metadata
        assert metadata["error"] == "Text has no sentences or words"


@pytest.mark.unit
def test_compute_score_simple_text(evaluator, mock_program):
    """Test compute_score with simple text."""
    # Simple text with known characteristics
    mock_program.get_source_files.return_value = {
        "main.txt": "This is a simple sentence. It has basic words."
    }

    # Mock the counting methods to return controlled values
    with (
        patch.object(evaluator, "_count_sentences", return_value=2),
        patch.object(evaluator, "_count_words", return_value=9),
        patch.object(evaluator, "_count_complex_words", return_value=0),
    ):
        score, metadata = evaluator._compute_score(mock_program)

        # Calculate expected GFI: 0.4 * ((9/2) + 100 * (0/9)) = 0.4 * 4.5 = 1.8
        # Normalized score: 1.0 - (1.8/20.0) = 0.91
        expected_score = 1.0 - (1.8 / 20.0)

        assert abs(score - expected_score) < 0.001
        assert "gunning_fog_index" in metadata
        assert abs(metadata["gunning_fog_index"] - 1.8) < 0.001
        assert metadata["sentences"] == 2
        assert metadata["words"] == 9
        assert metadata["complex_words"] == 0


@pytest.mark.unit
def test_compute_score_complex_text(evaluator, mock_program):
    """Test compute_score with more complex text."""
    # More complex text with known characteristics
    mock_program.get_source_files.return_value = {
        "main.txt": "The university professor discussed the utilization of computational resources."
    }

    # Mock the counting methods to return controlled values
    with (
        patch.object(evaluator, "_count_sentences", return_value=1),
        patch.object(evaluator, "_count_words", return_value=10),
        patch.object(evaluator, "_count_complex_words", return_value=3),
    ):
        score, metadata = evaluator._compute_score(mock_program)

        # Calculate expected GFI: 0.4 * ((10/1) + 100 * (3/10)) = 0.4 * (10 + 30) = 16
        # Normalized score: 1.0 - (16/20.0) = 0.2
        expected_score = 1.0 - (16 / 20.0)

        assert abs(score - expected_score) < 0.001
        assert "gunning_fog_index" in metadata
        assert abs(metadata["gunning_fog_index"] - 16.0) < 0.001
        assert metadata["sentences"] == 1
        assert metadata["words"] == 10
        assert metadata["complex_words"] == 3


@pytest.mark.unit
def test_compute_score_very_complex_text(evaluator, mock_program):
    """Test compute_score with text that exceeds the cap."""
    # Very complex text with characteristics that would exceed the cap
    mock_program.get_source_files.return_value = {
        "main.txt": "Antidisestablishmentarianism. Pneumonoultramicroscopicsilicovolcanoconiosis."
    }

    # Mock the counting methods to return values that would exceed the cap
    with (
        patch.object(evaluator, "_count_sentences", return_value=2),
        patch.object(evaluator, "_count_words", return_value=2),
        patch.object(evaluator, "_count_complex_words", return_value=2),
    ):
        score, metadata = evaluator._compute_score(mock_program)

        # Calculate expected GFI: 0.4 * ((2/2) + 100 * (2/2)) = 0.4 * (1 + 100) = 40.4
        # This exceeds our cap of 20, so score should be capped
        # Normalized score: 1.0 - (20/20.0) = 0.0
        expected_score = 0.0

        assert score == expected_score
        assert "gunning_fog_index" in metadata
        assert metadata["gunning_fog_index"] > 20.0  # Should be above cap
        assert metadata["sentences"] == 2
        assert metadata["words"] == 2
        assert metadata["complex_words"] == 2


@pytest.mark.unit
def test_logging(evaluator, mock_program, caplog):
    """Test that the evaluator logs appropriately."""
    caplog.set_level(logging.DEBUG)

    # Set up a valid text
    mock_program.get_source_files.return_value = {
        "main.txt": "This is a test. It has two sentences."
    }

    evaluator._compute_score(mock_program)

    # Check for debug log message
    assert "Computed Gunning Fog Index:" in caplog.text

    # Test warning for empty text
    caplog.clear()
    mock_program.get_source_files.return_value = {"main.txt": ""}

    evaluator._compute_score(mock_program)

    # Check for warning log message
    assert "Program text is empty or not a string" in caplog.text
