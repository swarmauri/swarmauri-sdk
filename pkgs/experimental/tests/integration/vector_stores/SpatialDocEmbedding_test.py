import pytest
from swarmauri_experimental.embeddings.SpatialDocEmbedding import (
    SpatialDocEmbedding,
)


@pytest.mark.acceptance
def test_ubc_resource():
    def test():
        assert SpatialDocEmbedding().resource == "Embedding"

    test()


@pytest.mark.acceptance
def test_fit_transform():
    embedder = SpatialDocEmbedding()
    embedder.fit_transform(["test", "test1", "test2"])
    assert embedder.infer_vector("test4").resource == "Vector"
