import pytest
from swarmauri_standard.embeddings.NmfEmbedding import NmfEmbedding


@pytest.fixture(scope="module")
def nmf_embedder():
    return NmfEmbedding()


@pytest.mark.unit
def test_ubc_resource(nmf_embedder):
    assert nmf_embedder.resource == "Embedding"


@pytest.mark.unit
def test_ubc_type(nmf_embedder):
    assert nmf_embedder.type == "NmfEmbedding"


@pytest.mark.unit
def test_serialization(nmf_embedder):
    assert (
        nmf_embedder.id
        == NmfEmbedding.model_validate_json(nmf_embedder.model_dump_json()).id
    )


@pytest.mark.unit
def test_fit_transform(nmf_embedder):
    documents = ["test", "test1", "test2"]
    nmf_embedder.fit_transform(documents)
    assert documents == nmf_embedder.extract_features()
