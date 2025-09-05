import pytest

from FastTokenizer.normalizer import (
    Normalizer,
    lowercase,
    normalize_unicode,
    remove_punctuation,
)


@pytest.fixture
def normalizer_instance():
    """Fixture to create an instance of the Normalizer class."""
    return Normalizer()


@pytest.mark.unit
class TestNormalizer:
    """Unit tests for the Normalizer class."""

    def test_init(self, normalizer_instance: Normalizer) -> None:
        """Test the initialization of the Normalizer class."""
        assert isinstance(normalizer_instance, Normalizer)

    @pytest.mark.parametrize(
        "input_string, expected_output",
        [
            ("Hello, World!", "hello, world!"),
            ("PYTHON IS AWESOME", "python is awesome"),
            ("123 ABC", "123 abc"),
        ],
    )
    @pytest.mark.unit
    def test_lowercase(self, input_string: str, expected_output: str) -> None:
        """Test the lowercase function."""
        result = lowercase(input_string)
        assert result == expected_output

    @pytest.mark.parametrize(
        "input_string, expected_output",
        [
            ("Hello, World!", "Hello World"),
            ("PYTHON IS AWESOME", "PYTHON IS AWESOME"),
            ("123 ABC", "123 ABC"),
        ],
    )
    @pytest.mark.unit
    def test_remove_punctuation(self, input_string: str, expected_output: str) -> None:
        """Test the remove_punctuation function."""
        result = remove_punctuation(input_string)
        assert result == expected_output

    @pytest.mark.parametrize(
        "input_string, expected_output",
        [
            ("Hello, World!", "hello, world"),
            ("PYTHON IS AWESOME", "python is awesome"),
            ("123 ABC", "123 abc"),
        ],
    )
    @pytest.mark.unit
    def test_normalize_unicode(self, input_string: str, expected_output: str) -> None:
        """Test the normalize_unicode function."""
        result = normalize_unicode(input_string)
        assert result == expected_output

    @pytest.mark.unit
    def test_normalizer_instance_methods(self, normalizer_instance: Normalizer) -> None:
        """Test the methods of the Normalizer instance."""
        input_string = "Hello, World!"
        assert normalizer_instance.lowercase(input_string) == "hello, world!"
        assert normalizer_instance.remove_punctuation(input_string) == "Hello World"
        assert normalizer_instance.normalize_unicode(input_string) == "hello, world"
