from swarmauri.documents.Document import Document
from swarmauri.vectorstores.PersistentQdrantVectorStore import (
    PersistentQdrantVectorStore,
)
from swarmauri.vector_stores.CloudQdrantVectorStore import (
    CloudQdrantVectorStore,
)

# Local Persistent Storage
local_store = PersistentQdrantVectorStore(
    collection_name="my_collection",
    vector_size=100,
    path="http://localhost:6333",
)
local_store.connect()

# Cloud Storage
cloud_store = CloudQdrantVectorStore(
    api_key="your_api_key",
    collection_name="my_collection",
    vector_size=100,
    url="your_qdrant_cloud_url",
)
cloud_store.connect()

# Add documents
documents = [
    Document(content="sample text 1"),
    Document(content="sample text 2"),
]
local_store.add_documents(documents)

# Retrieve similar documents
results = local_store.retrieve("sample query", top_k=5)
