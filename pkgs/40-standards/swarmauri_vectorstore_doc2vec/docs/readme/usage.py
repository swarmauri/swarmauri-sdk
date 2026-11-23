from swarmauri.vectorstores.Doc2VecVectorStore import Doc2VecVectorStore
from swarmauri.documents.Document import Document


# Initialize vector store
vector_store = Doc2VecVectorStore()

# Add documents
documents = [
    Document(content="This is the first document"),
    Document(content="Here is another document"),
    Document(content="And a third document"),
]
vector_store.add_documents(documents)

# Retrieve similar documents
results = vector_store.retrieve(query="document", top_k=2)
