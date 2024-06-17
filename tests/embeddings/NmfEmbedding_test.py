import pytest
from swarmauri.standard.embeddings.concrete.NmfEmbedding import NmfEmbedding

@pytest.mark.unit
def test_ubc_resource():
    def test():
        assert NmfEmbedding().resource == 'Embedding'
    test()

@pytest.mark.unit
def test_1():
	def test():
		embedder = NmfEmbedding()
		embedder.fit_transform(['test', 'test1', 'test2'])
		assert ['test2', 'test1', 'test'] == embedder.extract_features()
	test()