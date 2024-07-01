import pytest
from swarmauri.experimental.embeddings.SpatialDocEmbedding import SpatialDocEmbedding

@pytest.mark.acceptance
def test_ubc_resource():
    def test():
        assert SpatialDocEmbedding().resource == 'Embedding'
    test()

@pytest.mark.unit
def test_ubc_type():
	assert SpatialDocEmbedding().type == 'SpatialDocEmbedding'

@pytest.mark.unit
def test_serialization():
	embedder = SpatialDocEmbedding()
	assert embedder.id == SpatialDocEmbedding.model_validate_json(embedder.json()).id

@pytest.mark.acceptance
def test_fit_transform():
	embedder = SpatialDocEmbedding()
	embedder.fit_transform(['test', 'test1', 'test2'])
	assert type(embedder.infer_vector('test4')) == float