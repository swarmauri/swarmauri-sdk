import pytest
from swarmauri.embeddings.concrete.MlmEmbedding import MlmEmbedding

@pytest.mark.unit
def test_ubc_resource():
	assert MlmEmbedding().resource == 'Embedding'

@pytest.mark.unit
def test_ubc_type():
	assert MlmEmbedding().type == 'MlmEmbedding'

@pytest.mark.unit
def test_serialization():
	embedder = MlmEmbedding()
	assert embedder.id == MlmEmbedding.model_validate_json(embedder.model_dump_json()).id


@pytest.mark.unit
def test_fit_transform():
	embedder = MlmEmbedding()
	documents = ['test', 'test1', 'test2']
	embedder.fit_transform(documents)
	assert len(embedder.extract_features()) == 30522