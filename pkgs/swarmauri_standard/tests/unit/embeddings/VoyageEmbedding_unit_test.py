import os
import pytest
from swarmauri_standard.embeddings.VoyageEmbedding import VoyageEmbedding
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture(scope="module")
def voyage_embedder():
    API_KEY = os.getenv("VOYAGE_API_KEY")
    if not API_KEY:
        pytest.skip("Skipping due to environment variable not set")

    embedder = VoyageEmbedding(api_key=API_KEY)
    return embedder


@pytest.mark.unit
def test_voyage_resource(voyage_embedder):
    assert voyage_embedder.resource == "Embedding"


@pytest.mark.unit
def test_voyage_type(voyage_embedder):
    assert voyage_embedder.type == "VoyageEmbedding"


@pytest.mark.unit
def test_voyage_serialization(voyage_embedder):
    assert (
        voyage_embedder.id
        == VoyageEmbedding.model_validate_json(voyage_embedder.model_dump_json()).id
    )


@pytest.mark.unit
def test_voyage_infer_vector(voyage_embedder):
    documents = ["test", "cat", "banana"]
    response = voyage_embedder.transform(documents)
    assert 3 == len(response)
    assert float is type(response[0].value[0])
    assert 1024 == len(
        response[0].value
    )  # 1024 is the embedding size for voyage-2 model
