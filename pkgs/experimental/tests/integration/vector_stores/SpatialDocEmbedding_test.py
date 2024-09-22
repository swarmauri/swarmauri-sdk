import pytest
from swarmauri_experimental.embeddings.SpatialDocEmbedding import (
    SpatialDocEmbedding,
)


@pytest.mark.unit
def test_ubc_resource():
    assert SpatialDocEmbedding().resource == "Embedding"

@pytest.mark.xfail('Expected to fail until we fix the bug.')
def test_fit_transform():
    embedder = SpatialDocEmbedding()
    embedder.fit_transform(["test", "test1", "test2"])
    assert embedder.infer_vector("test4").resource == "Vector"
