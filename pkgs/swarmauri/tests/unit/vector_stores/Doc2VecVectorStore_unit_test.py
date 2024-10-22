import pytest
from swarmauri.documents.concrete.Document import Document
from swarmauri.vector_stores.concrete.Doc2VecVectorStore import Doc2VecVectorStore


@pytest.mark.unit
def test_ubc_resource():
    vs = Doc2VecVectorStore()
    assert vs.resource == "VectorStore"
    assert vs.embedder.resource == "Embedding"


@pytest.mark.unit
def test_ubc_type():
    vs = Doc2VecVectorStore()
    assert vs.type == "Doc2VecVectorStore"


@pytest.mark.unit
def test_serialization():
    vs = Doc2VecVectorStore()
    assert vs.id == Doc2VecVectorStore.model_validate_json(vs.model_dump_json()).id


@pytest.mark.unit
def test_top_k():
    vs = Doc2VecVectorStore()
    documents = [
        Document(content="test"),
        Document(content="test1"),
        Document(content="test2"),
        Document(content="test3"),
    ]

    vs.add_documents(documents)
    assert len(vs.retrieve(query="test", top_k=2)) == 2


@pytest.mark.unit
def test_adding_more_doc():
    vs = Doc2VecVectorStore()
    documents_batch_1 = [
        Document(content="test"),
        Document(content="test1"),
        Document(content="test2"),
        Document(content="test3"),
    ]
    documents_batch_2 = [
        Document(content="This is a test. Test number 4"),
        Document(content="This is a test. Test number 5"),
        Document(content="This is a test. Test number 6"),
        Document(content="This is a test. Test number 7"),
    ]
    doc_count = len(documents_batch_1) + len(documents_batch_2)

    vs.add_documents(documents_batch_1)
    vs.add_documents(documents_batch_2)
    assert len(vs.retrieve(query="test", top_k=doc_count)) == doc_count


@pytest.mark.unit
def test_oov():
    """Test for Out Of Vocabulary (OOV) words"""
    vs = Doc2VecVectorStore()
    documents = [
        Document(content="test"),
        Document(content="test1"),
        Document(content="test2"),
        Document(content="test3"),
    ]
    vs.add_documents(documents)
    assert len(vs.retrieve(query="what is test 4", top_k=2)) == 2
