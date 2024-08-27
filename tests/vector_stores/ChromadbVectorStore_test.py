import os
import pytest
from swarmauri.standard.documents.concrete.Document import Document
from swarmauri.community.vector_stores.ChromaDBVectorStore import ChromaDBVectorStore  

URL = os.getenv("Chromadb_URL_KEY")  
API_KEY = os.getenv("Chromadb_API_KEY")
COLLECTION_NAME = os.getenv("Chromadb_COLLECTION_NAME")

@pytest.mark.unit
def test_ubc_resource():
    vs = ChromaDBVectorStore(  
        url=URL,
        api_key=API_KEY,
        collection_name=COLLECTION_NAME,
        vector_size=100,
    )
    assert vs.resource == "VectorStore"
    assert vs.embedder.resource == "Embedding"

@pytest.mark.unit
def test_ubc_type():
    vs = ChromaDBVectorStore( 
        url=URL,
        api_key=API_KEY,
        collection_name=COLLECTION_NAME,
        vector_size=100,
    )
    assert vs.type == "ChromaDBVectorStore"

@pytest.mark.unit
def test_serialization():
    vs = ChromaDBVectorStore( 
        url=URL,
        api_key=API_KEY,
        collection_name=COLLECTION_NAME,
        vector_size=100,
    )
    assert vs.id == ChromaDBVectorStore.model_validate_json(vs.model_dump_json()).id  

@pytest.mark.unit
def top_k_test():
    vs = ChromaDBVectorStore( 
        url=URL,
        api_key=API_KEY,
        collection_name=COLLECTION_NAME,
        vector_size=100,
    )
    documents = [
        Document(content="test"),
        Document(content="test1"),
        Document(content="test2"),
        Document(content="test3"),
    ]

    vs.add_documents(documents)
    assert len(vs.retrieve(query="test", top_k=2)) == 2
