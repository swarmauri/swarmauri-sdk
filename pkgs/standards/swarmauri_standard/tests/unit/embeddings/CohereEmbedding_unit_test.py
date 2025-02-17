import os

import pytest
from dotenv import load_dotenv
from swarmauri_standard.embeddings.CohereEmbedding import CohereEmbedding

load_dotenv()
API_KEY = os.getenv("COHERE_API_KEY")


@pytest.fixture(scope="module")
def cohere_embedding():
    if not API_KEY:
        pytest.skip("Skipping due to environment variable not set")
    return CohereEmbedding(api_key=API_KEY)


@pytest.mark.unit
def test_ubc_resource(cohere_embedding):
    assert cohere_embedding.resource == "Embedding"


@pytest.mark.unit
def test_ubc_type(cohere_embedding):
    assert cohere_embedding.type == "CohereEmbedding"


@pytest.mark.unit
def test_serialization(cohere_embedding):
    assert (
        cohere_embedding.id
        == CohereEmbedding.model_validate_json(cohere_embedding.model_dump_json()).id
    )


@pytest.mark.unit
def test_infer(cohere_embedding):
    documents = ["test", "cat", "banana"]
    response = cohere_embedding.infer_vector(documents)
    assert 3 == len(response)
    assert float is type(response[0].value[0])
    assert 1024 == len(response[0].value)
