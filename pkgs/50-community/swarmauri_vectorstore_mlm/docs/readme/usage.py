from swarmauri.documents.Document import Document
from swarmauri.vector_stores.MlmVectorStore import MlmVectorStore

# Initialize the vector store
vs = MlmVectorStore()

# Create some documents
documents = [
    Document(content="first document"),
    Document(content="second document"),
    Document(content="third document"),
]

# Add documents to the store
vs.add_documents(documents)

# Retrieve similar documents
results = vs.retrieve(query="document", top_k=2)
