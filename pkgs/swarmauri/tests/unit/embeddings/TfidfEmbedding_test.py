import pytest
from swarmauri.embeddings.concrete.TfidfEmbedding import TfidfEmbedding

@pytest.mark.unit
def test_ubc_resource():
    def test():
        assert TfidfEmbedding().resource == 'Embedding'
    test()

@pytest.mark.unit
def test_ubc_type():
	assert TfidfEmbedding().type == 'TfidfEmbedding'

@pytest.mark.unit
def test_serialization():
	embedder = TfidfEmbedding()
	assert embedder.id == TfidfEmbedding.model_validate_json(embedder.model_dump_json()).id

@pytest.mark.unit
def test_fit_transform():
	embedder = TfidfEmbedding()
	documents = ['test', 'test1', 'test2']
	embedder.fit_transform(documents)
	assert documents == embedder.extract_features()

@pytest.mark.unit
def test_infer_vector():
	embedder = TfidfEmbedding()
	documents = ['test', 'test1', 'test2']
	embedder.fit_transform(documents)
	assert embedder.infer_vector('hi', documents).value == [1.0, 0.0, 0.0, 0.0]
	 