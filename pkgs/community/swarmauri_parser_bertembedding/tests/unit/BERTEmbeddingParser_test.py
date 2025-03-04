import numpy as np
import pytest
from swarmauri_parser_bertembedding.BERTEmbeddingParser import (
    BERTEmbeddingParser as Parser,
)

from swarmauri_standard.documents.Document import Document


@pytest.fixture(scope="module")
def parser():
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
    parser = Parser()

    # Test with a simple string input
    sample_text = "This is a test sentence for BERT embeddings."
    results = parser.parse(sample_text)

    # Basic structure checks
    assert isinstance(results, list), "Result should be a list of documents"
    assert len(results) > 0, "Parser should return at least one document"
    assert isinstance(results[0], Document), "Result should contain Document instances"

    # Check that content is the original text
    assert results[0].content == sample_text, "Content should be the original text"

    # Check the embeddings properties in metadata
    assert "embedding" in results[0].metadata, "Metadata should contain embedding"
    embedding = results[0].metadata["embedding"]
    assert isinstance(embedding, np.ndarray), "Embedding should be a numpy array"
    assert embedding.ndim == 1, "Embedding should be a 1D array (mean across tokens)"
    assert embedding.shape[0] == 768, (
        "BERT base model produces 768-dimensional embeddings"
    )

    # Check metadata
    assert "source" in results[0].metadata, "Metadata should contain source information"
    assert results[0].metadata["source"] == "BERTEmbeddingParser", (
        "Source should be BERTEmbeddingParser"
    )

    # Test with a list of strings (batch processing)
    batch_texts = [
        "First sentence.",
        "Second completely different text.",
        "Third example.",
    ]
    batch_results = parser.parse(batch_texts)

    assert isinstance(batch_results, list), "Batch result should be a list"
    assert len(batch_results) == len(batch_texts), (
        "Should return one document per input text"
    )

    # Verify embeddings are different for different texts
    first_embedding = batch_results[0].metadata["embedding"]
    second_embedding = batch_results[1].metadata["embedding"]

    # Calculate cosine similarity
    similarity = np.dot(first_embedding, second_embedding) / (
        np.linalg.norm(first_embedding) * np.linalg.norm(second_embedding)
    )

    # Different texts should have somewhat different embeddings
    assert similarity < 0.95, "Different texts should produce distinct embeddings"

    # Verify document contents match input
    for i, doc in enumerate(batch_results):
        assert doc.content == batch_texts[i], (
            f"Document {i} content should match input text"
        )
        assert doc.id == str(i), f"Document {i} should have ID '{i}'"
