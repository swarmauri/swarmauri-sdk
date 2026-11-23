from swarmauri.vector_stores.PineconeVectorStore import PineconeVectorStore
from swarmauri.documents.Document import Document

# Initialize vector store
vector_store = PineconeVectorStore(
    api_key="your-pinecone-api-key", collection_name="example", vector_size=100
)
vector_store.connect()

# Add documents
documents = [
    Document(content="First document"),
    Document(content="Second document"),
]
vector_store.add_documents(documents)

# Retrieve similar documents
results = vector_store.retrieve(query="document", top_k=2)
