from swarmauri.vector_stores.AnnoyVectorStore import AnnoyVectorStore
from swarmauri_standard.documents.Document import Document

# Initialize vector store
vector_store = AnnoyVectorStore(
    collection_name="my_collection", vector_size=100
)
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
