import logging
from unittest.mock import MagicMock

import pytest
from swarmauri_evaluatorpool_accessibility.FleschKincaidGradeEvaluator import (
    FleschKincaidGradeEvaluator,
)

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.fixture
def evaluator():
    """
    Fixture that provides a FleschKincaidGradeEvaluator instance.

    Returns:
        FleschKincaidGradeEvaluator: An instance of the evaluator
    """
    return FleschKincaidGradeEvaluator()


@pytest.fixture
def mock_program():
    """
    Fixture that provides a mock Program object.

    Returns:
        MagicMock: A mock Program instance
    """
    program = MagicMock()
    program.get_source_files.return_value = {"main.txt": ""}
    return program


@pytest.mark.unit
def test_type(evaluator):
    """
    Test that the evaluator has the correct type.

    Args:
        evaluator: The FleschKincaidGradeEvaluator instance
    """
    assert evaluator.type == "FleschKincaidGradeEvaluator"


@pytest.mark.unit
def test_resource(evaluator):
    """
    Test that the evaluator has the correct resource type.

    Args:
        evaluator: The FleschKincaidGradeEvaluator instance
    """
    assert evaluator.resource == "Evaluator"


@pytest.mark.unit
def test_serialization(evaluator):
    """
    Test that the evaluator can be serialized and deserialized correctly.

    Args:
        evaluator: The FleschKincaidGradeEvaluator instance
    """
    json_data = evaluator.model_dump_json()
    deserialized = FleschKincaidGradeEvaluator.model_validate_json(json_data)
    assert deserialized.type == evaluator.type
    assert deserialized.resource == evaluator.resource


@pytest.mark.unit
@pytest.mark.parametrize(
    "text, expected_sentences",
    [
        ("This is a sentence. This is another sentence.", 2),
        ("Hello world!", 1),
        ("What? How? When?", 3),
        ("", 0),
        ("No sentence terminators", 1),
    ],
)
def test_count_sentences(evaluator, text, expected_sentences):
    """
    Test the _count_sentences method with various text inputs.

    Args:
        evaluator: The FleschKincaidGradeEvaluator instance
        text: Input text to test
        expected_sentences: Expected number of sentences
    """
    assert evaluator._count_sentences(text) == expected_sentences


@pytest.mark.unit
@pytest.mark.parametrize(
    "text, expected_words",
    [
        ("This is a test.", 4),
        ("Hello, world!", 2),
        ("", 0),
        ("One", 1),
        ("Multiple   spaces   between   words", 4),
    ],
)
def test_count_words(evaluator, text, expected_words):
    """
    Test the _count_words method with various text inputs.

    Args:
        evaluator: The FleschKincaidGradeEvaluator instance
        text: Input text to test
        expected_words: Expected number of words
    """
    assert evaluator._count_words(text) == expected_words


@pytest.mark.unit
@pytest.mark.parametrize(
    "word, expected_syllables",
    [
        ("hello", 2),
        ("world", 1),
        ("education", 4),
        ("university", 5),
        ("", 0),
        ("a", 1),
    ],
)
def test_count_word_syllables(evaluator, word, expected_syllables):
    """
    Test the _count_word_syllables method with various words.

    Args:
        evaluator: The FleschKincaidGradeEvaluator instance
        word: Input word to test
        expected_syllables: Expected number of syllables
    """
    assert evaluator._count_word_syllables(word) == expected_syllables


@pytest.mark.unit
@pytest.mark.parametrize(
    "text, expected_syllables",
    [
        ("This is a test", 4),
        ("Hello world", 3),
        ("", 0),
        ("Education is important", 8),
    ],
)
def test_count_syllables(evaluator, text, expected_syllables):
    """
    Test the _count_syllables method with various text inputs.

    Args:
        evaluator: The FleschKincaidGradeEvaluator instance
        text: Input text to test
        expected_syllables: Expected number of syllables
    """
    assert evaluator._count_syllables(text) == expected_syllables


@pytest.mark.unit
@pytest.mark.parametrize(
    "output, expected_text",
    [
        ("Simple string", "Simple string"),
        ({"text": "Text in dict"}, "Text in dict"),
        ({"content": "Content in dict"}, "Content in dict"),
        (["Item1", "Item2"], "Item1 Item2"),
        (123, "123"),
    ],
)
def test_get_program_text(evaluator, mock_program, output, expected_text):
    """
    Test the _get_program_text method with various program outputs.

    Args:
        evaluator: The FleschKincaidGradeEvaluator instance
        mock_program: Mock Program object
        output: The mock output to test
        expected_text: Expected extracted text
    """
    mock_program.get_source_files.return_value = {"main.txt": output}
    result = evaluator._get_program_text(mock_program)
    assert result == expected_text


@pytest.mark.unit
def test_compute_score_with_valid_text(evaluator, mock_program):
    """
    Test the _compute_score method with valid text input.

    Args:
        evaluator: The FleschKincaidGradeEvaluator instance
        mock_program: Mock Program object
    """
    # Sample text with known characteristics
    test_text = "This is a simple sentence. It has two sentences with simple words."
    mock_program.get_source_files.return_value = {"main.txt": test_text}

    score, metadata = evaluator._compute_score(mock_program)

    # Verify the score is a float
    assert isinstance(score, float)

    # Verify metadata contains expected keys
    assert "sentences" in metadata
    assert "words" in metadata
    assert "syllables" in metadata
    assert "avg_sentence_length" in metadata
    assert "avg_syllables_per_word" in metadata

    # Verify counts
    assert metadata["sentences"] == 2
    assert metadata["words"] == 12


@pytest.mark.unit
def test_compute_score_with_empty_text(evaluator, mock_program):
    """
    Test the _compute_score method with empty text input.

    Args:
        evaluator: The FleschKincaidGradeEvaluator instance
        mock_program: Mock Program object
    """
    mock_program.get_source_files.return_value = {"main.txt": ""}

    score, metadata = evaluator._compute_score(mock_program)

    assert score == 0.0
    assert "error" in metadata
    assert metadata["error"] == "No text to evaluate"


@pytest.mark.unit
def test_compute_score_with_insufficient_content(evaluator, mock_program):
    """
    Test the _compute_score method with text that has insufficient content for analysis.

    Args:
        evaluator: The FleschKincaidGradeEvaluator instance
        mock_program: Mock Program object
    """
    # A string without any sentence terminators or proper structure
    mock_program.get_source_files.return_value = {"main.txt": "a"}

    score, metadata = evaluator._compute_score(mock_program)

    logging.info(f"Score: {score}, Metadata: {metadata}")

    # The score should be calculated even for minimal content
    assert isinstance(score, float)
    assert metadata["sentences"] == 1
    assert metadata["words"] == 1


@pytest.mark.unit
def test_formula_calculation(evaluator, mock_program):
    """
    Test that the FKGL formula is correctly applied.

    Args:
        evaluator: The FleschKincaidGradeEvaluator instance
        mock_program: Mock Program object
    """
    # Create text with known characteristics for predictable formula calculation
    test_text = "This is a test. This is another test. This is a third test."
    mock_program.get_source_files.return_value = {"main.txt": test_text}

    score, metadata = evaluator._compute_score(mock_program)

    # Manual calculation of the formula
    words_per_sentence = metadata["words"] / metadata["sentences"]
    syllables_per_word = metadata["syllables"] / metadata["words"]
    expected_score = max(
        0, 0.39 * words_per_sentence + 11.8 * syllables_per_word - 15.59
    )

    # Allow for small floating-point differences
    assert abs(score - expected_score) < 0.001

    # Verify formula components
    assert (
        abs(metadata["formula_calculation"]["term1"] - (0.39 * words_per_sentence))
        < 0.001
    )
    assert (
        abs(metadata["formula_calculation"]["term2"] - (11.8 * syllables_per_word))
        < 0.001
    )
    assert metadata["formula_calculation"]["constant"] == -15.59
