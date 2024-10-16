import os
import pytest
from swarmauri.embeddings.concrete.MistralEmbedding import MistralEmbedding

@pytest.mark.unit
def test_ubc_resource():
    assert MistralEmbedding().resource == "Embedding"


@pytest.mark.unit
def test_ubc_type():
    assert MistralEmbedding().type == "MistralEmbedding"


@pytest.mark.unit
def test_serialization():
    embedder = MistralEmbedding()
    assert (
        embedder.id
        == MistralEmbedding.model_validate_json(embedder.model_dump_json()).id
    )


@pytest.mark.unit
@pytest.mark.skipif(not os.getenv('MISTRAL_API_KEY'), reason="Skipping due to environment variable not set")
def test_infer():
    embedder = MistralEmbedding(api_key=os.getenv("MISTRAL_API_KEY"))
    documents = ["test", "cat", "banana"]
    response = embedder.infer_vector(documents)
    assert 3 == len(response)
    assert float == type(response[0].value[0])
    assert 1024 == len(response[0].value)
