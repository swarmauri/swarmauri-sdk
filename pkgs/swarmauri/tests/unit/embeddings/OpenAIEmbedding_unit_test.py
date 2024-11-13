import os
import pytest
from swarmauri.embeddings.concrete.OpenAIEmbedding import OpenAIEmbedding
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture(scope="module")
def openai_embedder():
    API_KEY = os.getenv("OPENAI_API_KEY")
    if not API_KEY:
        pytest.skip("Skipping due to environment variable not set")

    embedder = OpenAIEmbedding(
        api_key=API_KEY
    )  # Changed from OPENAI_API_KEY to api_key
    return embedder


@pytest.mark.unit
def test_ubc_resource(openai_embedder):
    assert openai_embedder.resource == "Embedding"


@pytest.mark.unit
def test_ubc_type(openai_embedder):
    assert openai_embedder.type == "OpenAIEmbedding"


@pytest.mark.unit
def test_serialization(openai_embedder):
    assert (
        openai_embedder.id
        == OpenAIEmbedding.model_validate_json(openai_embedder.model_dump_json()).id
    )


@pytest.mark.unit
def test_infer_vector(openai_embedder):
    documents = ["test", "cat", "banana"]
    response = openai_embedder.infer_vector(documents)
    assert 3 == len(response)
    assert float == type(response[0].value[0])
    assert 1536 == len(
        response[0].value
    )  # 1536 is the embedding size for text-embedding-3-small model
