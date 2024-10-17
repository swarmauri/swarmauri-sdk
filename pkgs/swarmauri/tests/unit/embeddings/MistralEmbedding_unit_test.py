import os
import pytest
from swarmauri.embeddings.concrete.MistralEmbedding import MistralEmbedding
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("MISTRAL_API_KEY")


@pytest.fixture(scope="module")
def mistral_embedder():
    if not API_KEY:
        pytest.skip("Skipping due to environment variable not set")
    return MistralEmbedding(api_key=API_KEY)


@pytest.mark.unit
def test_ubc_resource(mistral_embedder):
    assert mistral_embedder.resource == "Embedding"


@pytest.mark.unit
def test_ubc_type(mistral_embedder):
    assert mistral_embedder.type == "MistralEmbedding"


@pytest.mark.unit
def test_serialization(mistral_embedder):
    assert (
        mistral_embedder.id
        == MistralEmbedding.model_validate_json(mistral_embedder.model_dump_json()).id
    )


@pytest.mark.unit
def test_infer(mistral_embedder):
    documents = ["test", "cat", "banana"]
    response = mistral_embedder.infer_vector(documents)
    assert 3 == len(response)
    assert float == type(response[0].value[0])
    assert 1024 == len(response[0].value)
