import pytest
from swarmauri.embeddings.concrete.Doc2VecEmbedding import Doc2VecEmbedding

@pytest.mark.unit
def test_ubc_resource():
	assert Doc2VecEmbedding().resource == 'Embedding'

@pytest.mark.unit
def test_ubc_type():
	assert Doc2VecEmbedding().type == 'Doc2VecEmbedding'

@pytest.mark.unit
def test_serialization():
	embedder = Doc2VecEmbedding()
	assert embedder.id == Doc2VecEmbedding.model_validate_json(embedder.model_dump_json()).id

@pytest.mark.unit
def test_fit_transform():
	embedder = Doc2VecEmbedding()
	documents = ['test', 'cat', 'banana']
	embedder.fit_transform(documents)
	assert ['banana', 'cat', 'test'] == embedder.extract_features()