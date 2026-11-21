from swarmauri.documents.Document import Document
from swarmauri.vector_stores.Neo4jVectorStore import Neo4jVectorStore

# Initialize the vector store
store = Neo4jVectorStore(
    uri="neo4j://localhost:7687", user="neo4j", password="your_password"
)

# Add a document
doc = Document(
    id="doc1", content="Sample content", metadata={"author": "John Doe"}
)
store.add_document(doc)

# Retrieve similar documents
similar_docs = store.retrieve(query="sample", top_k=5)

# Close connection when done
store.close()
