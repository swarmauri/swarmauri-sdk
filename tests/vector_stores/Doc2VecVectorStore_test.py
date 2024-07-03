import pytest
from swarmauri.standard.documents.concrete.Document import Document
from swarmauri.standard.vector_stores.concrete.Doc2VecVectorStore import Doc2VecVectorStore

@pytest.mark.unit
def test_ubc_resource():
	vs = Doc2VecVectorStore()
	assert vs.resource == 'VectorStore'
	assert vs.embedder.resource == 'Embedding'

@pytest.mark.unit
def test_ubc_type():
	vs = Doc2VecVectorStore()
	assert vs.type == 'Doc2VecVectorStore'

@pytest.mark.unit
def test_serialization():
	vs = Doc2VecVectorStore()
	assert vs.id == Doc2VecVectorStore.model_validate_json(vs.model_dump_json()).id

@pytest.mark.unit
def top_k_test():
	vs = Doc2VecVectorStore()
	documents = [Document(content="test"),
	     Document(content='test1'),
	     Document(content='test2'),
	     Document(content='test3')]

	vs.add_documents(documents)
	assert len(vs.retrieve(query='test', top_k=2)) == 2
