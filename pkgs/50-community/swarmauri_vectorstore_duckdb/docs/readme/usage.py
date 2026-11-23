from swarmauri.vector_stores.DuckDBVectorStore import DuckDBVectorStore
from swarmauri.documents.Document import Document

# Initialize vector store
vector_store = DuckDBVectorStore(database_name="my_vectors.db")
vector_store.connect()

# Add documents
doc = Document(
    id="doc1",
    content="The quick brown fox jumps over the lazy dog",
    metadata={"type": "example"},
)
vector_store.add_document(doc)

# Retrieve similar documents
results = vector_store.retrieve("fox jumping", top_k=2)

# Clean up
vector_store.disconnect()
