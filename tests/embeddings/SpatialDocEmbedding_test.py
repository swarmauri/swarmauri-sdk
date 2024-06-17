import pytest
from swarmauri.experimental.embeddings.SpatialDocEmbedding import SpatialDocEmbedding

@pytest.mark.acceptance
def test_ubc_resource():
    def test():
        assert SpatialDocEmbedding().resource == 'Embedding'
    test()

@pytest.mark.acceptance
def test_1():
	def test():
		embedder = SpatialDocEmbedding()
		embedder.fit_transform(['test', 'test1', 'test2'])
		assert type(embedder.infer_vector('test4')) == float
	test()