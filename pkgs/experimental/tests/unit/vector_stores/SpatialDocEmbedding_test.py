import pytest
from swarmauri_experimental.embeddings.SpatialDocEmbedding import (
    SpatialDocEmbedding,
)


@pytest.mark.unit
def test_ubc_type():
    assert SpatialDocEmbedding().type == "SpatialDocEmbedding"


@pytest.mark.unit
def test_serialization():
    embedder = SpatialDocEmbedding()
    assert (
        embedder.id
        == SpatialDocEmbedding.model_validate_json(embedder.model_dump_json()).id
    )
