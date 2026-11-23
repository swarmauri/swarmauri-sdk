from swarmauri.documents.Document import Document
from swarmauri.vector_stores.PersistentChromaDBVectorStore import (
    PersistentChromaDBVectorStore,
)

# Initialize the vector store
vector_store = PersistentChromaDBVectorStore(
    path="./chromadb_data", collection_name="my_collection", vector_size=100
)

# Connect to the store
vector_store.connect()

# Add documents
documents = [
    Document(content="first document"),
    Document(content="second document"),
    Document(content="third document"),
]
vector_store.add_documents(documents)

# Retrieve similar documents
results = vector_store.retrieve(query="document", top_k=2)
