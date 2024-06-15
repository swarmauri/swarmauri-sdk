import pytest
from swarmauri.standard.embeddings.concrete.SpatialDocEmbedding import SpatialDocEmbedding

@pytest.mark.unit
def test_1():
	def test():
		embedder = SpatialDocEmbedding()
		embedder.fit_transform(['test', 'test1', 'test2'])
		assert type(infer_vector('poop1')) == float
	test()