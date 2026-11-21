from swarmauri_embedding_nmf import NmfEmbedding

documents = [
    "This is the first document",
    "This is the second document",
    "And this is the third one",
]

# n_components must not exceed the number of documents or unique terms
embedder = NmfEmbedding(n_components=3)

# Fit and transform the documents into Swarmauri Vector objects
vectors = embedder.fit_transform(documents)

for document, vector in zip(documents, vectors):
    print(document, vector.value)

print("Vocabulary:", embedder.extract_features())

# Transform a new document after fitting
new_vector = embedder.infer_vector("This is a new document")
print("New vector:", new_vector.value)
