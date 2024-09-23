import os
import pytest
from swarmauri.embeddings.concrete.OpenAIEmbedding import OpenAIEmbedding


@pytest.mark.unit
def test_ubc_resource():
    assert OpenAIEmbedding().resource == "Embedding"


@pytest.mark.unit
def test_ubc_type():
    assert OpenAIEmbedding().type == "OpenAIEmbedding"


@pytest.mark.unit
def test_serialization():
    embedder = OpenAIEmbedding()
    assert (
        embedder.id
        == OpenAIEmbedding.model_validate_json(embedder.model_dump_json()).id
    )


@pytest.mark.unit
def test_transform():
    embedder = OpenAIEmbedding(api_key=os.getenv("OPENAI_API_KEY"))
    documents = ["test", "cat", "banana"]
    response = embedder.transform(documents)
    assert 3 == len(response)
    assert float == type(response[0].value[0])
    assert 1536 == len(
        response[0].value
    )  # 1536 is the embedding size for text-embedding-3-small model
