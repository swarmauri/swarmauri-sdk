import pytest
from swarmauri.documents.concrete.Document import Document
from swarmauri_experimental.vector_stores.AnnoyVectorStore import AnnoyVectorStore

@pytest.mark.unit
def test_ubc_resource():
	vs = AnnoyVectorStore()
	assert vs.resource == 'VectorStore'
	assert vs.embedder.resource == 'Embedding'

@pytest.mark.unit
def test_ubc_type():
	vs = AnnoyVectorStore()
	assert vs.type == 'AnnoyVectorStore'

@pytest.mark.unit
def test_serialization():
	vs = AnnoyVectorStore()
	assert vs.id == AnnoyVectorStore.model_validate_json(vs.model_dump_json()).id

@pytest.mark.unit
def top_k_test():
	vs = AnnoyVectorStore()
	documents = [Document(content="test"),
	     Document(content='test1'),
	     Document(content='test2'),
	     Document(content='test3')]

	vs.add_documents(documents)
	assert len(vs.retrieve(query='test', top_k=2)) == 2
