from unittest.mock import MagicMock, patch

import pytest
from swarmauri_core.programs.IProgram import IProgram
from swarmauri_evaluatorpool_accessibility.AutomatedReadabilityIndexEvaluator import (
    AutomatedReadabilityIndexEvaluator,
)


@pytest.fixture
def evaluator():
    """
    Fixture that provides an instance of AutomatedReadabilityIndexEvaluator.

    Returns:
        AutomatedReadabilityIndexEvaluator: An instance of the evaluator
    """
    return AutomatedReadabilityIndexEvaluator()


@pytest.fixture
def mock_program():
    """
    Fixture that provides a mocked Program instance.

    Returns:
        MagicMock: A mock object that simulates a Program
    """
    program = MagicMock(spec=IProgram)
    program.name = "Test Program"
    # Add the missing get_artifacts method
    program.get_artifacts = MagicMock(return_value=[])
    return program


@pytest.mark.unit
def test_type_attribute():
    """Test that the type attribute is correctly set."""
    evaluator = AutomatedReadabilityIndexEvaluator()
    assert evaluator.type == "AutomatedReadabilityIndexEvaluator"


@pytest.mark.unit
def test_serialization(evaluator):
    """Test that the evaluator can be properly serialized and deserialized."""
    # Serialize
    json_data = evaluator.model_dump_json()

    # Deserialize
    deserialized = AutomatedReadabilityIndexEvaluator.model_validate_json(json_data)

    # Verify
    assert deserialized.type == evaluator.type


@pytest.mark.unit
def test_count_words(evaluator):
    """Test the _count_words method with various inputs."""
    test_cases = [
        ("This is a simple test.", ["this", "is", "a", "simple", "test"]),
        ("", []),
        ("One", ["one"]),
        ("Multiple    spaces    here", ["multiple", "spaces", "here"]),
        (
            "Hyphenated-words aren't counted correctly",
            ["hyphenated", "words", "aren", "t", "counted", "correctly"],
        ),
    ]

    for text, expected in test_cases:
        result = evaluator._count_words(text)
        assert result == expected


@pytest.mark.unit
def test_count_sentences(evaluator):
    """Test the _count_sentences method with various inputs."""
    test_cases = [
        ("This is one sentence.", ["This is one sentence."]),
        ("This is one. This is two.", ["This is one.", "This is two."]),
        ("Hello! How are you? I'm good.", ["Hello!", "How are you?", "I'm good."]),
        ("", []),
        ("No ending punctuation", ["No ending punctuation"]),
    ]

    for text, expected in test_cases:
        result = evaluator._count_sentences(text)
        assert result == expected


@pytest.mark.unit
def test_extract_text_from_program_empty(evaluator, mock_program):
    """Test text extraction when no artifacts are present."""
    mock_program.get_artifacts.return_value = []

    result = evaluator._extract_text_from_program(mock_program)

    assert result == ""
    mock_program.get_artifacts.assert_called_once()


@pytest.mark.unit
@patch("os.path.exists")
@patch("builtins.open")
def test_extract_text_from_program_txt(mock_open, mock_exists, evaluator, mock_program):
    """Test text extraction from a .txt file."""
    # Setup mocks
    mock_artifact = MagicMock()
    mock_artifact.get_path.return_value = "test.txt"
    mock_program.get_artifacts.return_value = [mock_artifact]
    mock_exists.return_value = True

    mock_file = MagicMock()
    mock_file.__enter__.return_value.read.return_value = "This is a test text file."
    mock_open.return_value = mock_file

    # Call function
    result = evaluator._extract_text_from_program(mock_program)

    # Assertions
    assert result == "This is a test text file."
    mock_program.get_artifacts.assert_called_once()
    mock_artifact.get_path.assert_called_once()
    mock_exists.assert_called_once_with("test.txt")
    mock_open.assert_called_once()


@pytest.mark.unit
@patch("os.path.exists")
@patch("builtins.open")
@patch("markdown.markdown")
@patch(
    "swarmauri_evaluatorpool_accessibility.AutomatedReadabilityIndexEvaluator.BeautifulSoup"
)
def test_extract_text_from_program_md(
    mock_soup, mock_markdown, mock_open, mock_exists, evaluator, mock_program
):
    """Test text extraction from a .md file."""
    # Setup mocks
    mock_artifact = MagicMock()
    mock_artifact.get_path.return_value = "test.md"
    mock_program.get_artifacts.return_value = [mock_artifact]
    mock_exists.return_value = True

    mock_file = MagicMock()
    mock_file.__enter__.return_value.read.return_value = "# Markdown Test"
    mock_open.return_value = mock_file

    mock_markdown.return_value = "<h1>Markdown Test</h1>"

    mock_soup_instance = MagicMock()
    mock_soup_instance.get_text.return_value = "Markdown Test"
    mock_soup.return_value = mock_soup_instance

    # Call function
    result = evaluator._extract_text_from_program(mock_program)

    # Assertions
    assert result == "Markdown Test"
    mock_program.get_artifacts.assert_called_once()
    mock_markdown.assert_called_once_with("# Markdown Test")
    mock_soup.assert_called_once_with("<h1>Markdown Test</h1>", "html.parser")


@pytest.mark.unit
@patch("os.path.exists")
@patch("builtins.open")
@patch(
    "swarmauri_evaluatorpool_accessibility.AutomatedReadabilityIndexEvaluator.BeautifulSoup"
)
def test_extract_text_from_program_html(
    mock_soup, mock_open, mock_exists, evaluator, mock_program
):
    """Test text extraction from a .html file."""
    # Setup mocks
    mock_artifact = MagicMock()
    mock_artifact.get_path.return_value = "test.html"
    mock_program.get_artifacts.return_value = [mock_artifact]
    mock_exists.return_value = True

    mock_file = MagicMock()
    mock_file.__enter__.return_value.read.return_value = (
        "<html><body>HTML Test</body></html>"
    )
    mock_open.return_value = mock_file

    mock_soup_instance = MagicMock()
    mock_soup_instance.get_text.return_value = "HTML Test"
    mock_soup.return_value = mock_soup_instance

    # Call function
    result = evaluator._extract_text_from_program(mock_program)

    # Assertions
    assert result == "HTML Test"
    mock_program.get_artifacts.assert_called_once()
    mock_soup.assert_called_once_with(
        "<html><body>HTML Test</body></html>", "html.parser"
    )


@pytest.mark.unit
@patch("os.path.exists")
def test_extract_text_from_program_file_error(mock_exists, evaluator, mock_program):
    """Test handling of file errors during text extraction."""
    # Setup mocks
    mock_artifact = MagicMock()
    mock_artifact.get_path.return_value = "test.txt"
    mock_program.get_artifacts.return_value = [mock_artifact]
    mock_exists.return_value = True

    # Mock open to raise an exception
    with patch("builtins.open", side_effect=Exception("File error")):
        # Call function
        result = evaluator._extract_text_from_program(mock_program)

    # Assertions
    assert result == ""
    mock_program.get_artifacts.assert_called_once()


@pytest.mark.unit
@patch.object(AutomatedReadabilityIndexEvaluator, "_extract_text_from_program")
def test_compute_score_no_content(mock_extract, evaluator, mock_program):
    """Test compute_score when no text content is found."""
    mock_extract.return_value = ""

    score, metadata = evaluator._compute_score(mock_program)

    assert score == 0.0
    assert "error" in metadata
    assert metadata["chars"] == 0
    assert metadata["words"] == 0
    assert metadata["sentences"] == 0
    mock_extract.assert_called_once_with(mock_program)


@pytest.mark.unit
@patch.object(AutomatedReadabilityIndexEvaluator, "_extract_text_from_program")
@patch.object(AutomatedReadabilityIndexEvaluator, "_count_words")
@patch.object(AutomatedReadabilityIndexEvaluator, "_count_sentences")
def test_compute_score_zero_words(
    mock_sentences, mock_words, mock_extract, evaluator, mock_program
):
    """Test compute_score when zero words are found."""
    mock_extract.return_value = "..."
    mock_words.return_value = []
    mock_sentences.return_value = ["..."]

    score, metadata = evaluator._compute_score(mock_program)

    assert score == 0.0
    assert "error" in metadata
    assert metadata["words"] == 0
    mock_extract.assert_called_once_with(mock_program)


@pytest.mark.unit
@patch.object(AutomatedReadabilityIndexEvaluator, "_extract_text_from_program")
@patch.object(AutomatedReadabilityIndexEvaluator, "_count_words")
@patch.object(AutomatedReadabilityIndexEvaluator, "_count_sentences")
def test_compute_score_zero_sentences(
    mock_sentences, mock_words, mock_extract, evaluator, mock_program
):
    """Test compute_score when zero sentences are found."""
    mock_extract.return_value = "test words"
    mock_words.return_value = ["test", "words"]
    mock_sentences.return_value = []

    score, metadata = evaluator._compute_score(mock_program)

    assert score == 0.0
    assert "error" in metadata
    assert metadata["sentences"] == 0
    mock_extract.assert_called_once_with(mock_program)


@pytest.mark.unit
@patch.object(AutomatedReadabilityIndexEvaluator, "_extract_text_from_program")
@patch.object(AutomatedReadabilityIndexEvaluator, "_count_words")
@patch.object(AutomatedReadabilityIndexEvaluator, "_count_sentences")
def test_compute_score_success(
    mock_sentences, mock_words, mock_extract, evaluator, mock_program
):
    """Test successful computation of ARI score."""
    mock_extract.return_value = (
        "This is a test sentence. This is another test sentence."
    )
    mock_words.return_value = [
        "this",
        "is",
        "a",
        "test",
        "sentence",
        "this",
        "is",
        "another",
        "test",
        "sentence",
    ]
    mock_sentences.return_value = [
        "This is a test sentence",
        "This is another test sentence.",
    ]

    score, metadata = evaluator._compute_score(mock_program)

    # Expected ARI calculation:
    # 4.71 * (chars/words) + 0.5 * (words/sentences) - 21.43
    # chars = 60, words = 10, sentences = 2
    # 4.71 * (60/10) + 0.5 * (10/2) - 21.43
    # 4.71 * 6 + 0.5 * 5 - 21.43
    # 28.26 + 2.5 - 21.43 = 9.33

    assert score > 0.0
    assert "chars" in metadata
    assert "words" in metadata
    assert "sentences" in metadata
    assert metadata["chars"] == len(mock_extract.return_value)
    assert metadata["words"] == len(mock_words.return_value)
    assert metadata["sentences"] == len(mock_sentences.return_value)

    # Verify the formula is applied correctly
    expected_score = (
        4.71 * (metadata["chars"] / metadata["words"])
        + 0.5 * (metadata["words"] / metadata["sentences"])
        - 21.43
    )
    expected_score = max(0.0, expected_score)
    assert (
        abs(score - expected_score) < 0.01
    )  # Allow for small floating point differences


@pytest.mark.unit
@patch.object(AutomatedReadabilityIndexEvaluator, "_extract_text_from_program")
@patch.object(AutomatedReadabilityIndexEvaluator, "_count_words")
@patch.object(AutomatedReadabilityIndexEvaluator, "_count_sentences")
def test_compute_score_negative_result(
    mock_sentences, mock_words, mock_extract, evaluator, mock_program
):
    """Test that compute_score never returns a negative score."""
    # Set up values that would produce a negative ARI score
    mock_extract.return_value = "a b c."  # Very short words
    mock_words.return_value = ["a", "b", "c"]
    mock_sentences.return_value = ["a b c."]

    score, metadata = evaluator._compute_score(mock_program)

    # The formula could produce a negative score, but we should clamp it to 0
    assert score == 0.0
    assert metadata["chars"] == len(mock_extract.return_value)
    assert metadata["words"] == len(mock_words.return_value)
    assert metadata["sentences"] == len(mock_sentences.return_value)
