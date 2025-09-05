from unittest.mock import MagicMock, patch
import json

import pytest
from swarmauri_evaluatorpool_accessibility.FleschReadingEaseEvaluator import (
    FleschReadingEaseEvaluator,
)


@pytest.fixture
def evaluator():
    """
    Fixture that provides a FleschReadingEaseEvaluator instance.

    Returns:
        FleschReadingEaseEvaluator: An instance of the evaluator
    """
    return FleschReadingEaseEvaluator()


@pytest.fixture
def mock_program():
    """
    Fixture that provides a mock Program object.

    Returns:
        MagicMock: A mock Program object with configurable content
    """
    program = MagicMock()
    program.get_source_files.return_value = {"main.txt": ""}
    return program


@pytest.mark.unit
def test_type(evaluator):
    """Test that the evaluator has the correct type."""
    assert evaluator.type == "FleschReadingEaseEvaluator"


@pytest.mark.unit
def test_initialization(evaluator):
    """Test that the evaluator initializes correctly."""
    assert isinstance(evaluator, FleschReadingEaseEvaluator)
    assert hasattr(evaluator, "cmu_dict")


@pytest.mark.unit
@patch("nltk.data.find")
@patch("nltk.download")
def test_nltk_resources_downloaded(mock_download, mock_find, evaluator):
    """Test that NLTK resources are downloaded if not found."""
    # Simulate resources not found
    mock_find.side_effect = LookupError()

    # Re-initialize to trigger downloads
    FleschReadingEaseEvaluator()

    # Verify downloads were attempted
    assert mock_download.call_count >= 1


@pytest.mark.unit
@pytest.mark.parametrize(
    "content, expected_score, expected_metadata_keys",
    [
        (
            "This is a simple sentence. It is easy to read.",
            pytest.approx(90, abs=15),
            [
                "sentence_count",
                "word_count",
                "syllable_count",
                "readability_interpretation",
            ],
        ),
        (
            "The mitochondria is the powerhouse of the cell. It produces ATP through oxidative phosphorylation.",
            pytest.approx(15, abs=10),
            [
                "sentence_count",
                "word_count",
                "syllable_count",
                "readability_interpretation",
            ],
        ),
        ("", 0.0, ["error"]),
    ],
)
def test_compute_score(
    evaluator, mock_program, content, expected_score, expected_metadata_keys
):
    """
    Test the _compute_score method with different text contents.

    Args:
        evaluator: The evaluator instance
        mock_program: A mock Program object
        content: The text content to evaluate
        expected_score: The expected Flesch Reading Ease score
        expected_metadata_keys: Expected keys in the metadata dictionary
    """
    mock_program.get_source_files.return_value = {"main.txt": content}

    score, metadata = evaluator._compute_score(mock_program)

    assert isinstance(score, float)
    if content:
        assert score == expected_score
    else:
        assert score == 0.0

    for key in expected_metadata_keys:
        assert key in metadata


@pytest.mark.unit
@pytest.mark.parametrize(
    "word, expected_count",
    [
        ("simple", 2),
        ("complicated", 4),
        ("the", 1),
        ("readability", 5),
        ("a", 1),
    ],
)
def test_count_syllables(evaluator, word, expected_count):
    """
    Test the syllable counting functionality.

    Args:
        evaluator: The evaluator instance
        word: The word to count syllables for
        expected_count: The expected syllable count
    """
    # Allow some flexibility in syllable counting since different methods may yield
    # slightly different results
    count = evaluator._count_syllables(word)
    assert count > 0  # Every word should have at least one syllable
    assert abs(count - expected_count) <= 1  # Allow off-by-one differences


@pytest.mark.unit
@pytest.mark.parametrize(
    "text, expected_output",
    [
        ("  Multiple    spaces   ", "Multiple spaces"),
        ("\t\nWhitespace\r\n", "Whitespace"),
        ("Normal text", "Normal text"),
    ],
)
def test_clean_text(evaluator, text, expected_output):
    """
    Test the text cleaning functionality.

    Args:
        evaluator: The evaluator instance
        text: The input text to clean
        expected_output: The expected cleaned text
    """
    cleaned = evaluator._clean_text(text)
    assert cleaned == expected_output


@pytest.mark.unit
@pytest.mark.parametrize(
    "score, expected_category",
    [
        (95, "Very Easy"),
        (85, "Easy"),
        (75, "Fairly Easy"),
        (65, "Standard"),
        (55, "Fairly Difficult"),
        (40, "Difficult"),
        (20, "Very Difficult"),
    ],
)
def test_interpret_score(evaluator, score, expected_category):
    """
    Test the score interpretation functionality.

    Args:
        evaluator: The evaluator instance
        score: The Flesch Reading Ease score
        expected_category: The expected readability category
    """
    interpretation = evaluator._interpret_score(score)
    assert expected_category in interpretation


@pytest.mark.unit
def test_compute_score_with_non_string_content(evaluator, mock_program):
    """
    Test that the evaluator handles non-string content gracefully.

    Args:
        evaluator: The evaluator instance
        mock_program: A mock Program object
    """
    mock_program.get_source_files.return_value = {
        "main.txt": 12345
    }  # Non-string content

    score, metadata = evaluator._compute_score(mock_program)

    assert score == 0.0
    assert "error" in metadata


@pytest.mark.unit
def test_serialization(evaluator):
    """
    Test that the evaluator can be serialized and deserialized correctly.

    Args:
        evaluator: The evaluator instance
    """
    serialized = evaluator.model_dump_json()
    deserialized = FleschReadingEaseEvaluator.model_validate_json(serialized)

    assert deserialized.type == evaluator.type
    assert "cmu_dict" not in json.loads(serialized)
