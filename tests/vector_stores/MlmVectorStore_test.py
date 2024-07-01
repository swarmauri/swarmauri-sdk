import pytest
from swarmauri.standard.documents.concrete.Document import Document
from swarmauri.standard.vector_stores.concrete.MlmVectorStore import MlmVectorStore

@pytest.mark.unit
def test_ubc_resource():
	vs = MlmVectorStore()
	assert vs.type == 'VectorStore'
	assert vs.embedder.resource == 'Embedding'

@pytest.mark.unit
def test_ubc_type():
	vs = MlmVectorStore()
    assert vs.type == 'MlmVectorStore'

@pytest.mark.unit
def test_serialization():
    vs = MlmVectorStore()
    assert vs.id == MlmVectorStore.model_validate_json(vs.model_dump()).id

@pytest.mark.unit
def top_k_test():
	vs = MlmVectorStore()
	documents = [Document(content="test"),
	     Document(content='test1'),
	     Document(content='test2'),
	     Document(content='test3')]

	vs.add_documents(documents)
	assert len(vs.retrieve(query='test', top_k=2)) == 2

@pytest.mark.unit
def load_from_json_test():
	vs = MlmVectorStore()
	documents = [Document(content="test"),
	     Document(content='test1'),
	     Document(content='test2'),
	     Document(content='test3')]

	vs.add_documents(documents)
	vs_2 = MlmVectorStore.parse_raw(vs.model_dump())
	assert vs.id == vs_2.id
	assert vs.document_count() == vs_2.document_count()
