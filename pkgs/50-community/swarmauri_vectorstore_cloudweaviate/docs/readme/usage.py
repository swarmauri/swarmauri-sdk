from swarmauri.vector_stores.CloudWeaviateVectorStore import (
    CloudWeaviateVectorStore,
)
from swarmauri.documents.Document import Document

# Initialize the vector store
vector_store = CloudWeaviateVectorStore(
    url="your-weaviate-url",
    api_key="your-api-key",
    collection_name="example",
    vector_size=100,
)

# Connect to Weaviate
vector_store.connect()

# Add documents
document = Document(
    id="doc-001",
    content="This is a sample document content.",
    metadata={"author": "Alice", "date": "2024-01-01"},
)
vector_store.add_document(document)

# Retrieve similar documents
results = vector_store.retrieve(query="sample content", top_k=5)

# Clean up
vector_store.disconnect()
