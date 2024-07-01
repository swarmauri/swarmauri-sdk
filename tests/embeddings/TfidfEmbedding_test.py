import pytest
from swarmauri.standard.embeddings.concrete.TfidfEmbedding import TfidfEmbedding

@pytest.mark.unit
def test_ubc_resource():
    def test():
        assert TfidfEmbedding().resource == 'Embedding'
    test()

@pytest.mark.unit
def test_ubc_type():
	assert TfidfEmbedding().type == 'Doc2VecEmbedding'

@pytest.mark.unit
def test_serialization():
	embedder = TfidfEmbedding()
	assert embedder.id == TfidfEmbedding.model_validate_json(embedder.json()).id

@pytest.mark.unit
def test_fit_transform():
	embedder = TfidfEmbedding()
	documents = ['test', 'test1', 'test2']
	embedder.fit_transform(documents)
	assert documents == embedder.extract_features()