import os
import pytest
from dotenv import load_dotenv
from swarmauri.documents.concrete.Document import Document
from swarmauri_community.vector_stores.Neo4jVectorStore import Neo4jVectorStore

# Load environment variables
load_dotenv()
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
COLLECTION_NAME = os.getenv("NEO4J_COLLECTION_NAME", "TestCollection")


@pytest.mark.skipif(
    not os.getenv("NEO4J_PASSWORD"),
    reason="Skipping due to environment variable not set",
)
@pytest.fixture(scope="module")
def vector_store():
    """
    Fixture to initialize and teardown the Neo4jVectorStore.
    """
    if not all([NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD]):
        pytest.fail(
            "NEO4J_URI, NEO4J_USER, and NEO4J_PASSWORD must be set in environment variables."
        )

    store = Neo4jVectorStore(
        uri=NEO4J_URI,
        user=NEO4J_USER,
        password=NEO4J_PASSWORD,
        collection_name=COLLECTION_NAME,  # If applicable
    )
    yield store
    # Teardown: Clean up the test collection if necessary
    try:
        with store._driver.session() as session:
            session.run(
                """
                MATCH (d:Document)
                DETACH DELETE d
            """
            )
    except Exception as e:
        pytest.fail(f"Teardown failed: {e}")
    store.close()


@pytest.mark.skipif(
    not os.getenv("NEO4J_PASSWORD"),
    reason="Skipping due to environment variable not set",
)
@pytest.fixture
def sample_documents():
    return [
        Document(
            id="doc_sample_1", content="Sample Content 1", metadata={"key": "value1"}
        ),
        Document(
            id="doc_sample_2", content="Sample Content 2", metadata={"key": "value2"}
        ),
    ]


@pytest.mark.unit
def test_ubc_type(vector_store):
    """
    Test to verify the type attribute of Neo4jVectorStore.
    """
    assert vector_store.type == "Neo4jVectorStore"


@pytest.mark.skipif(
    not os.getenv("NEO4J_PASSWORD"),
    reason="Skipping due to environment variable not set",
)
@pytest.mark.unit
def test_serialization(vector_store):
    """
    Test to verify serialization and deserialization of Neo4jVectorStore.
    """
    assert (
        vector_store.id
        == Neo4jVectorStore.model_validate_json(vector_store.model_dump_json()).id
    )


@pytest.mark.skipif(
    not os.getenv("NEO4J_PASSWORD"),
    reason="Skipping due to environment variable not set",
)
@pytest.mark.unit
def top_k_test(vector_store):
    documents = [
        Document(id="doc_test_1", content="test", metadata={}),
        Document(id="doc_test_2", content="test1", metadata={}),
        Document(id="doc_test_3", content="test2", metadata={}),
        Document(id="doc_test_4", content="test3", metadata={}),
    ]

    vector_store.add_documents(documents)
    retrieved_docs = vector_store.retrieve(query="test", top_k=2)
    assert len(retrieved_docs) == 2
    # Assuming 'doc_test_1' and 'doc_test_2' are the most similar
    expected_ids = {"doc_test_1", "doc_test_2"}
    retrieved_ids = {doc.id for doc in retrieved_docs}
    assert retrieved_ids == expected_ids


@pytest.mark.unit
def test_add_document(vector_store):
    doc = Document(
        id="doc_add_1",
        content="This is a sample document.",
        metadata={"author": "John Doe", "title": "Sample Document"},
    )
    vector_store.add_document(doc)
    retrieved_doc = vector_store.get_document("doc_add_1")
    assert retrieved_doc == doc


@pytest.mark.unit
def test_add_documents(vector_store, sample_documents):
    vector_store.add_documents(sample_documents)
    for doc in sample_documents:
        retrieved_doc = vector_store.get_document(doc.id)
        assert retrieved_doc == doc
