import pytest
import numpy as np
from swarmauri.documents.concrete.Document import Document
from swarmauri_community.vector_stores.RedisVectorStore import RedisVectorStore  

@pytest.fixture(scope="module")
def vector_store():
    vector_store = RedisVectorStore(
    redis_host="redis-12648.c305.ap-south-1-1.ec2.redns.redis-cloud.com",
    redis_port=12648,
    redis_password='EaNg3YcgUW94Uj1P5wT3LScNtM97avu2',  # Replace with your password if needed
    embedding_dimension=8000  # Adjust based on your embedder
)
    return vector_store

# Create a sample document
@pytest.fixture
def sample_document():
    return Document(
        id="test_doc1",
        content="This is a test document for unit testing.",
        metadata={"category": "test"}
    )

@pytest.mark.unit
def test_ubc_resource():
    vs = RedisVectorStore(
    redis_host="redis-12648.c305.ap-south-1-1.ec2.redns.redis-cloud.com",
    redis_port=12648,
    redis_password='EaNg3YcgUW94Uj1P5wT3LScNtM97avu2',  # Replace with your password if needed
    embedding_dimension=8000  # Adjust based on your embedder
    )
    assert vs.resource == 'VectorStore'

@pytest.mark.unit
def test_ubc_type():
    vs = RedisVectorStore(redis_host="redis-12648.c305.ap-south-1-1.ec2.redns.redis-cloud.com",
    redis_port=12648,
    redis_password='EaNg3YcgUW94Uj1P5wT3LScNtM97avu2',  
    embedding_dimension=8000)
    assert vs.type == 'RedisVectorStore'
    

@pytest.mark.unit
def top_k_test(vs = vector_store):
	documents = [Document(content="test"),
	     Document(content='test1'),
	     Document(content='test2'),
	     Document(content='test3')]

	vs.add_documents(documents)
	assert len(vs.retrieve(query='test', top_k=2)) == 2


@pytest.mark.unit
def test_add_and_get_document(vector_store, sample_document):
    vector_store.add_document(sample_document)

    retrieved_doc = vector_store.get_document("test_doc1")
    
    assert retrieved_doc is not None
    assert retrieved_doc.id == "test_doc1"
    assert retrieved_doc.content == "This is a test document for unit testing."
    assert retrieved_doc.metadata == {"category": "test"}



@pytest.mark.unit
def test_delete_document(vector_store, sample_document):
    vector_store.add_document(sample_document)
    vector_store.delete_document("test_doc1")
    
    retrieved_doc = vector_store.get_document("test_doc1")
    assert retrieved_doc is None


@pytest.mark.unit
def test_retrieve_similar_documents(vector_store):
    doc1 = Document(id="doc1", content="Sample document content about testing.", metadata={"category": "sample"})
    doc2 = Document(id="doc2", content="Another test document for retrieval.", metadata={"category": "sample"})
    
    vector_store.add_document(doc1)
    vector_store.add_document(doc2)
    
    similar_docs = vector_store.retrieve("test document", top_k=2)
    
    assert len(similar_docs) == 2
    assert similar_docs[0].id == "doc1" or similar_docs[0].id == "doc2"
    assert similar_docs[1].id == "doc1" or similar_docs[1].id == "doc2"
