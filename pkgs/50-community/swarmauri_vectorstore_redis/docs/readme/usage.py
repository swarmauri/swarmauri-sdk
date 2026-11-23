from swarmauri.vector_stores.RedisVectorStore import RedisVectorStore
from swarmauri.documents.Document import Document

# Initialize the vector store
vector_store = RedisVectorStore(
    redis_host="localhost",
    redis_port=6379,
    redis_password="your_password",
    embedding_dimension=8000,
)

# Add documents
document = Document(
    id="doc1",
    content="Sample document content",
    metadata={"category": "sample"},
)
vector_store.add_document(document)

# Retrieve similar documents
similar_docs = vector_store.retrieve("sample content", top_k=5)
