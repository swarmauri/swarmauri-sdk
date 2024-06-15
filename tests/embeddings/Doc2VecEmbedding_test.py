import pytest
from swarmauri.standard.embeddings.concrete.Doc2VecEmbedding import Doc2VecEmbedding

@pytest.mark.unit
def ubc_initialization_test():
    def test():
        assert Doc2VecEmbedding().resource == 'Embedding'
    test()

@pytest.mark.unit
def test_1():
	def test():
		embedder = Doc2VecEmbedding()
		embedder.fit_transform(['test', 'test1', 'test2'])
		assert ['test2', 'test1', 'test'] == embedder.extract_features()
	test()