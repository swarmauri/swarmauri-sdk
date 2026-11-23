import fasttokenizer
import pytest


@pytest.mark.i9n
def test_native_tokenizer():
    tokenizer = fasttokenizer.WhitespaceTokenizer()
    assert tokenizer.tokenize("hello world") == ["hello", "world"]


@pytest.mark.i9n
def test_native_normalization():
    assert fasttokenizer.lowercase("Swarmauri") == "swarmauri"


@pytest.mark.i9n
def test_native_module_version():
    assert isinstance(fasttokenizer.__version__, str)
    assert fasttokenizer.__version__
