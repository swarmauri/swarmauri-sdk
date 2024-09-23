import pytest
from swarmauri.embeddings.concrete.NmfEmbedding import NmfEmbedding

@pytest.mark.unit
def test_ubc_resource():
	assert NmfEmbedding().resource == 'Embedding'

@pytest.mark.unit
def test_ubc_type():
	assert NmfEmbedding().type == 'NmfEmbedding'

@pytest.mark.unit
def test_serialization():
	embedder = NmfEmbedding()
	assert embedder.id == NmfEmbedding.model_validate_json(embedder.model_dump_json()).id

@pytest.mark.unit
def test_fit_transform():
	embedder = NmfEmbedding()
	documents = ['test', 'test1', 'test2']
	embedder.fit_transform(documents)
	assert documents == embedder.extract_features()