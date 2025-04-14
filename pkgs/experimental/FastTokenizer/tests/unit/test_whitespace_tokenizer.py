import logging
import pytest
from FastTokenizer.whitespace_tokenizer import whitespace_tokenizer

# Setting up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@pytest.fixture
def sample_text():
    """Fixtures for sample text inputs."""
    return {
        "simple": "This is a sample text.",
        "with_whitespace": "This\tis\na sample\textended\tover\nmultiple\nlines.",
        "empty": "",
        "whitespace_only": "    \t\n  ",
        "mixed": "Hello, World! This is a test.\nWith multiple lines and\ttabs."
    }

@pytest.mark.unit
def test_whitespace_tokenizer_simple(sample_text):
    """
    Test whitespace_tokenizer with simple text.

    Args:
        sample_text (dict): Contains sample text inputs.

    Returns:
        None
    """
    text = sample_text["simple"]
    expected = ["This", "is", "a", "sample", "text."]
    result = whitespace_tokenizer(text)
    assert result == expected, f"Expected {expected}, got {result}"

@pytest.mark.unit
def test_whitespace_tokenizer_with_whitespace(sample_text):
    """
    Test whitespace_tokenizer with various whitespace characters.

    Args:
        sample_text (dict): Contains sample text inputs.

    Returns:
        None
    """
    text = sample_text["with_whitespace"]
    expected = [
        "This", "is", "a", "sample", "extended", "over", "multiple", "lines."
    ]
    result = whitespace_tokenizer(text)
    assert result == expected, f"Expected {expected}, got {result}"

@pytest.mark.unit
def test_whitespace_tokenizer_empty(sample_text):
    """
    Test whitespace_tokenizer with empty text.

    Args:
        sample_text (dict): Contains sample text inputs.

    Returns:
        None
    """
    text = sample_text["empty"]
    expected = []
    result = whitespace_tokenizer(text)
    assert result == expected, f"Expected {expected}, got {result}"

@pytest.mark.unit
def test_whitespace_tokenizer_whitespace_only(sample_text):
    """
    Test whitespace_tokenizer with whitespace-only text.

    Args:
        sample_text (dict): Contains sample text inputs.

    Returns:
        None
    """
    text = sample_text["whitespace_only"]
    expected = []
    result = whitespace_tokenizer(text)
    assert result == expected, f"Expected {expected}, got {result}"

@pytest.mark.unit
def test_whitespace_tokenizer_mixed(sample_text):
    """
    Test whitespace_tokenizer with mixed content.

    Args:
        sample_text (dict): Contains sample text inputs.

    Returns:
        None
    """
    text = sample_text["mixed"]
    expected = [
        "Hello,", "World!", "This", "is", "a", "test.",
        "With", "multiple", "lines", "and", "tabs."
    ]
    result = whitespace_tokenizer(text)
    assert result == expected, f"Expected {expected}, got {result}"

@pytest.mark.unit
@pytest.mark.parametrize("text,expected", [
    ("SingleWord", ["SingleWord"]),
    ("Multiple   Words", ["Multiple", "Words"]),
    ("Tabs\tand\nNewlines", ["Tabs", "and", "Newlines"]),
])
def test_whitespace_tokenizer_varied(text, expected):
    """
    Test whitespace_tokenizer with varied inputs.

    Args:
        text (str): Input text to tokenize.
        expected (list): Expected tokenized output.

    Returns:
        None
    """
    result = whitespace_tokenizer(text)
    assert result == expected, f"Expected {expected}, got {result}"