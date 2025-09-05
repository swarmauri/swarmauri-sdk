import logging
import pytest
from FastTokenizer.regex_tokenizer import RegexTokenizer

# Set up logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.mark.unit
class TestRegexTokenizer:
    """Unit tests for the RegexTokenizer class."""

    @pytest.fixture
    def regex_tokenizer(self):
        """Create a RegexTokenizer instance with a default pattern."""
        return RegexTokenizer(pattern=r"\w+")

    def test_init(self, regex_tokenizer):
        """Test that the RegexTokenizer instance is created correctly."""
        assert regex_tokenizer.get_pattern() == r"\w+"

    def test_tokenize(self, regex_tokenizer):
        """Test that the tokenize method returns the expected tokens."""
        input_string = "This is a test string."
        expected_tokens = ["This", "is", "a", "test", "string"]
        tokens = regex_tokenizer.tokenize(input_string)
        assert tokens == expected_tokens

    @pytest.mark.parametrize("input_string, expected_tokens", [
        ("Hello world!", ["Hello", "world"]),
        ("This is another test.", ["This", "is", "another", "test"]),
    ])
    def test_tokenize_multiple(self, regex_tokenizer, input_string, expected_tokens):
        """Test that the tokenize method returns the expected tokens for multiple inputs."""
        tokens = regex_tokenizer.tokenize(input_string)
        assert tokens == expected_tokens

    def test_get_pattern(self, regex_tokenizer):
        """Test that the get_pattern method returns the expected regex pattern."""
        assert regex_tokenizer.get_pattern() == r"\w+"

    def test_invalid_pattern(self):
        """Test that an invalid regex pattern raises a ValueError."""
        with pytest.raises(ValueError):
            RegexTokenizer(pattern="[Invalid pattern")

    def test_none_pattern(self):
        """Test that a None regex pattern raises a ValueError."""
        with pytest.raises(ValueError):
            RegexTokenizer(pattern=None)