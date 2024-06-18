import pytest
from swarmauri.standard.embeddings.concrete.Doc2VecEmbedding import Doc2VecEmbedding

@pytest.mark.unit
def test_ubc_resource():
    def test():
        assert Doc2VecEmbedding().resource == 'Embedding'
    test()

@pytest.mark.unit
def test_fit_transform():
	def test():
		embedder = Doc2VecEmbedding()
		documents = ['test', 'test1', 'test2']
		embedder.fit_transform(documents)
		assert documents == embedder.extract_features()
	test()