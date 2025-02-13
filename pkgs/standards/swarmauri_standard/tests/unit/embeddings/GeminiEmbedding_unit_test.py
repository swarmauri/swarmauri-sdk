import os

import pytest
from dotenv import load_dotenv
from swarmauri_standard.embeddings.GeminiEmbedding import GeminiEmbedding

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")


@pytest.fixture
def gemini_embedding(scope="module"):
    if not API_KEY:
        pytest.skip("Skipping due to environment variable not set")
    return GeminiEmbedding(api_key=API_KEY)


@pytest.mark.unit
def test_ubc_resource(gemini_embedding):
    assert gemini_embedding.resource == "Embedding"


@pytest.mark.unit
def test_ubc_type(gemini_embedding):
    assert gemini_embedding.type == "GeminiEmbedding"


@pytest.mark.unit
def test_serialization(gemini_embedding):
    assert (
        gemini_embedding.id
        == GeminiEmbedding.model_validate_json(gemini_embedding.model_dump_json()).id
    )


@pytest.mark.unit
def test_infer(gemini_embedding):
    documents = ["test", "cat", "banana"]
    response = gemini_embedding.infer_vector(documents)
    assert 3 == len(response)
    assert float is type(response[0].value[0])
    assert 768 == len(response[0].value)
