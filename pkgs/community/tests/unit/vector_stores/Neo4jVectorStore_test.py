import os
import pytest
from dotenv import load_dotenv
from swarmauri.documents.concrete.Document import Document
from swarmauri_community.vector_stores.Neo4jVectorStore import Neo4jVectorStore


load_dotenv()
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
COLLECTION_NAME = os.getenv("NEO4J_COLLECTION_NAME", "TestCollection")


@pytest.mark.skipif(
    not os.getenv("NEO4J_PASSWORD"),
    reason="Skipping due to environment variable not set",
)
@pytest.fixture(scope="module")
def vector_store():
    """
    Fixture to initialize and teardown the Neo4jVectorStoreLevenshtein.
    """
    store = Neo4jVectorStore(
        uri=NEO4J_URI,
        user=NEO4J_USER,
        password=NEO4J_PASSWORD,
        collection_name=COLLECTION_NAME,  # If applicable
    )
    yield store
    # # Teardown: Clean up the test collection if necessary
    # with store._driver.session() as session:
    #     session.run("""
    #         MATCH (d:Document)
    #         DETACH DELETE d
    #     """)
    store.close()


@pytest.mark.skipif(
    not os.getenv("NEO4J_PASSWORD"),
    reason="Skipping due to environment variable not set",
)
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
        Document(content="test"),
        Document(content="test1"),
        Document(content="test2"),
        Document(content="test3"),
    ]

    vector_store.add_documents(documents)
    assert len(vector_store.retrieve(query="test", top_k=2)) == 2
