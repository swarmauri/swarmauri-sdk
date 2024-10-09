import os
import pytest
from swarmauri.embeddings.concrete.CohereEmbedding import CohereEmbedding
from dotenv import load_dotenv

load_dotenv()


@pytest.mark.unit
def test_ubc_resource():
    assert CohereEmbedding().resource == "Embedding"


@pytest.mark.unit
def test_ubc_type():
    assert CohereEmbedding().type == "CohereEmbedding"


@pytest.mark.unit
def test_serialization():
    embedder = CohereEmbedding()
    assert (
        embedder.id
        == CohereEmbedding.model_validate_json(embedder.model_dump_json()).id
    )


@pytest.mark.unit
@pytest.mark.skipif(not os.getenv('COHERE_API_KEY'), reason="Skipping due to environment variable not set")
def test_infer():
    embedder = CohereEmbedding(api_key=os.getenv("COHERE_API_KEY"))
    documents = ["test", "cat", "banana"]
    response = embedder.infer_vector(documents)
    assert 3 == len(response)
    assert float == type(response[0].value[0])
    assert 1024 == len(response[0].value)
