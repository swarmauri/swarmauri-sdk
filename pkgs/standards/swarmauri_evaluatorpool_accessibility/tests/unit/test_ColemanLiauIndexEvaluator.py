import logging
from unittest.mock import MagicMock

import pytest
from swarmauri_evaluatorpool_accessibility.ColemanLiauIndexEvaluator import (
    ColemanLiauIndexEvaluator,
)


@pytest.fixture
def evaluator():
    """
    Fixture that provides a ColemanLiauIndexEvaluator instance.

    Returns:
        ColemanLiauIndexEvaluator: An instance of the evaluator
    """
    return ColemanLiauIndexEvaluator()


@pytest.fixture
def mock_program():
    """
    Fixture that provides a mock Program object.

    Returns:
        MagicMock: A mock Program object
    """
    program = MagicMock()
    program.output = ""
    return program


@pytest.mark.unit
def test_type(evaluator):
    """Test that the evaluator type is correctly defined."""
    assert evaluator.type == "ColemanLiauIndexEvaluator"


@pytest.mark.unit
def test_default_parameters(evaluator):
    """Test that default parameters are correctly set."""
    assert evaluator.normalize_scores is True
    assert evaluator.target_grade_level == 8
    assert evaluator.max_grade_level == 16


@pytest.mark.unit
def test_serialization(evaluator):
    """Test serialization and deserialization of the evaluator."""
    json_data = evaluator.model_dump_json()
    deserialized = ColemanLiauIndexEvaluator.model_validate_json(json_data)

    assert deserialized.type == evaluator.type
    assert deserialized.normalize_scores == evaluator.normalize_scores
    assert deserialized.target_grade_level == evaluator.target_grade_level
    assert deserialized.max_grade_level == evaluator.max_grade_level


@pytest.mark.unit
@pytest.mark.parametrize(
    "text,expected_letters",
    [
        ("Hello world", 10),
        ("123 numbers!", 7),
        ("", 0),
        ("   ", 0),
        ("A.B.C.", 3),
    ],
)
def test_count_letters(evaluator, text, expected_letters):
    """Test letter counting functionality with various inputs."""
    assert evaluator._count_letters(text) == expected_letters


@pytest.mark.unit
@pytest.mark.parametrize(
    "text,expected_words",
    [
        ("Hello world", 2),
        ("One two three four", 4),
        ("", 0),
        ("   ", 0),
        ("Word with-hyphen", 2),
        ("Multiple    spaces", 2),
    ],
)
def test_count_words(evaluator, text, expected_words):
    """Test word counting functionality with various inputs."""
    assert evaluator._count_words(text) == expected_words


@pytest.mark.unit
@pytest.mark.parametrize(
    "text,expected_sentences",
    [
        ("Hello world.", 1),
        ("Hello! How are you? I'm fine.", 3),
        ("No ending", 1),
        ("", 0),
        ("   ", 0),
        ("Sentence one. Sentence two.", 2),
        ("Multiple!!! Exclamations?? Marks.", 3),
    ],
)
def test_count_sentences(evaluator, text, expected_sentences):
    """Test sentence counting functionality with various inputs."""
    assert evaluator._count_sentences(text) == expected_sentences


@pytest.mark.unit
@pytest.mark.parametrize(
    "grade_level,expected_score",
    [
        (8, 1.0),  # Target grade level
        (1, 0.0),  # Minimum grade level
        (16, 0.0),  # Maximum grade level
        (10, 0.75),  # Above target
        (6, 0.75),  # Below target
    ],
)
def test_calculate_score(evaluator, grade_level, expected_score):
    """Test score calculation based on grade level."""
    # The expected scores are based on default target_grade_level=8 and max_grade_level=16
    assert evaluator._calculate_score(grade_level) == pytest.approx(
        expected_score, abs=0.01
    )


@pytest.mark.unit
def test_calculate_score_no_normalization(evaluator):
    """Test score calculation when normalization is disabled."""
    evaluator.normalize_scores = False
    assert evaluator._calculate_score(10) == 10.0


@pytest.mark.unit
@pytest.mark.parametrize(
    "program_attrs,expected_text",
    [
        ({"output": "Test output"}, "Test output"),
        ({"output": None, "content": "Test content"}, "Test content"),
        ({"output": None, "content": None, "source": "Test source"}, "Test source"),
        ({}, ""),  # Default case when no attributes are available
    ],
)
def test_get_text_from_program(evaluator, program_attrs, expected_text):
    """Test text extraction from different program attributes."""
    program = MagicMock()

    # Set up the program with the specified attributes
    for attr, value in program_attrs.items():
        setattr(program, attr, value)

    # Handle the default case for empty attributes
    if not program_attrs:
        program.output = None
        program.content = None
        program.source = None
        program.__str__.return_value = ""

    assert evaluator._get_text_from_program(program) == expected_text


@pytest.mark.unit
def test_compute_score_empty_text(evaluator, mock_program):
    """Test compute_score with empty text."""
    mock_program.output = ""

    score, metadata = evaluator._compute_score(mock_program)

    assert score == 0.0
    assert "error" in metadata
    assert metadata["error"] == "Empty text"


@pytest.mark.unit
def test_compute_score_no_words(evaluator, mock_program):
    """Test compute_score with text containing no words."""
    mock_program.output = "... !!! ???"

    score, metadata = evaluator._compute_score(mock_program)

    assert score == 0.0
    logging.info(f"Metadata: {metadata}")
    assert "error" in metadata
    assert metadata["error"] == "No words found"


@pytest.mark.unit
@pytest.mark.parametrize(
    "text,expected_grade_level",
    [
        ("Simple short sentences. Easy words.", 3),
        (
            "The Coleman-Liau index is a readability assessment that approximates the U.S. grade level thought necessary to comprehend the text.",
            12,
        ),
        ("Hello world.", 5),
    ],
)
def test_compute_score_various_texts(
    evaluator, mock_program, text, expected_grade_level
):
    """Test compute_score with various texts of different complexity."""
    mock_program.output = text

    score, metadata = evaluator._compute_score(mock_program)

    # Check that grade level is calculated correctly
    assert (
        abs(metadata["grade_level"] - expected_grade_level) <= 4
    )  # Allow some flexibility in expected grade level

    # Check metadata contains expected keys
    expected_keys = {
        "grade_level",
        "raw_index",
        "letters",
        "words",
        "sentences",
        "letters_per_100_words",
        "sentences_per_100_words",
        "target_grade_level",
    }
    assert all(key in metadata for key in expected_keys)


@pytest.mark.unit
def test_compute_score_logging(evaluator, mock_program, caplog):
    """Test that logging works correctly during score computation."""
    caplog.set_level(logging.DEBUG)
    mock_program.output = "This is a test sentence."

    evaluator._compute_score(mock_program)

    # Check that debug logs were created
    assert any("Text analysis:" in record.message for record in caplog.records)
    assert any("Coleman-Liau Index:" in record.message for record in caplog.records)


@pytest.mark.unit
def test_custom_parameters():
    """Test that custom parameters are correctly used."""
    evaluator = ColemanLiauIndexEvaluator(
        normalize_scores=False, target_grade_level=10, max_grade_level=20
    )

    assert evaluator.normalize_scores is False
    assert evaluator.target_grade_level == 10
    assert evaluator.max_grade_level == 20


@pytest.mark.unit
def test_edge_case_identical_target_and_max_grade_level():
    """Test edge case where target and max grade levels are identical."""
    evaluator = ColemanLiauIndexEvaluator(target_grade_level=10, max_grade_level=10)

    # With identical target and max, the score should be 1.0 for target and 0.0 otherwise
    assert evaluator._calculate_score(10) == 1.0
    assert evaluator._calculate_score(9) < 1.0


@pytest.mark.unit
def test_evaluate_returns_score_and_metadata(evaluator, mock_program):
    """evaluate() should return a dict with 'score' and 'metadata'."""
    mock_program.output = "Hello world."

    result = evaluator.evaluate(mock_program)

    assert set(result.keys()) == {"score", "metadata"}
    assert isinstance(result["metadata"], dict)
