# Import all symbols from the Rust extension
from .fasttokenizer import *  # noqa: F403

# You can add pure Python code or additional exports here


def whitespace_tokenizer(text: str) -> list[str]:
    """Split text using the Rust whitespace tokenizer."""
    from .fasttokenizer import WhitespaceTokenizer

    return WhitespaceTokenizer().tokenize(text)
