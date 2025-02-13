import pytest
from swarmauri_standard.embeddings.TfidfEmbedding import TfidfEmbedding


@pytest.fixture(scope="module")
def tfidf_embedder():
    return TfidfEmbedding()


@pytest.mark.unit
def test_ubc_resource(tfidf_embedder):
    assert tfidf_embedder.resource == "Embedding"


@pytest.mark.unit
def test_ubc_type(tfidf_embedder):
    assert tfidf_embedder.type == "TfidfEmbedding"


@pytest.mark.unit
def test_serialization(tfidf_embedder):
    assert (
        tfidf_embedder.id == TfidfEmbedding.model_validate_json(tfidf_embedder.model_dump_json()).id
    )


@pytest.mark.unit
def test_fit_transform(tfidf_embedder):
    documents = ["test", "test1", "test2"]
    tfidf_embedder.fit_transform(documents)
    assert documents == tfidf_embedder.extract_features()


@pytest.mark.unit
def test_infer_vector(tfidf_embedder):
    documents = ["test", "test1", "test2"]
    tfidf_embedder.fit_transform(documents)
    assert tfidf_embedder.infer_vector("hi", documents).value == [1.0, 0.0, 0.0, 0.0]
