import pytest
from swarmauri_parser_bertembedding.BERTEmbeddingParser import (
    BERTEmbeddingParser as Parser,
)
import numpy as np


@pytest.fixture(scope="module")
def parser():
    """Fixture to provide a parser instance for tests."""
    return Parser()


@pytest.mark.unit
def test_ubc_resource(parser):
    assert parser.resource == "Parser"


@pytest.mark.unit
def test_ubc_type(parser):
    assert parser.type == "BERTEmbeddingParser"


@pytest.mark.unit
def test_serialization(parser):
    assert parser.id == Parser.model_validate_json(parser.model_dump_json()).id


@pytest.mark.unit
def test_parse(parser):
    # Test basic text parsing
    text = "This is a test sentence."
    documents = parser.parse(text)

    # Verify basic properties
    assert len(documents) == 1
    doc = documents[0]
    assert doc.resource == "Document"
    assert isinstance(doc.content, np.ndarray)
    assert doc.content.shape == (768,)  # BERT base embedding size
    assert doc.metadata["source"] == "BERTEmbeddingParser"
    assert isinstance(doc.id, str)


@pytest.mark.unit
def test_parse_empty(parser):
    # Test empty input
    with pytest.raises(ValueError):
        parser.parse("")


@pytest.mark.unit
def test_parse_long_text(parser):
    # Test text longer than 512 tokens
    long_text = " ".join(["word"] * 1000)
    documents = parser.parse(long_text)
    assert len(documents) == 1
    assert documents[0].content.shape == (768,)


@pytest.mark.unit
def test_parse_special_chars(parser):
    # Test text with special characters
    special_text = "Hello! @#$%^&* World 123"
    documents = parser.parse(special_text)
    assert len(documents) == 1
    assert documents[0].content.shape == (768,)
