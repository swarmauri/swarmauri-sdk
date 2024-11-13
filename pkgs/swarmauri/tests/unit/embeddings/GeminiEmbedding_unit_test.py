import os
import pytest
from swarmauri.embeddings.concrete.GeminiEmbedding import GeminiEmbedding
from dotenv import load_dotenv

load_dotenv()


@pytest.mark.unit
def test_ubc_resource():
    assert GeminiEmbedding().resource == "Embedding"


@pytest.mark.unit
def test_ubc_type():
    assert GeminiEmbedding().type == "GeminiEmbedding"


@pytest.mark.unit
def test_serialization():
    embedder = GeminiEmbedding()
    assert (
        embedder.id
        == GeminiEmbedding.model_validate_json(embedder.model_dump_json()).id
    )


@pytest.mark.unit
@pytest.mark.skipif(
    not os.getenv("GEMINI_API_KEY"),
    reason="Skipping due to environment variable not set",
)
def test_infer():
    embedder = GeminiEmbedding(api_key=os.getenv("GEMINI_API_KEY"))
    documents = ["test", "cat", "banana"]
    response = embedder.infer_vector(documents)
    assert 3 == len(response)
    assert float == type(response[0].value[0])
    assert 768 == len(response[0].value)
