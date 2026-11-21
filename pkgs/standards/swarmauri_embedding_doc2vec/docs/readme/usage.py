from swarmauri_embedding_doc2vec import Doc2VecEmbedding

documents = [
    "This is the first document.",
    "Here is another document.",
    "And a third one.",
]

# Initialize the embedder. Adjust parameters to match your dataset size.
embedder = Doc2VecEmbedding(vector_size=300, window=10, min_count=1, workers=1)

# Fit and transform documents into Vector objects.
vectors = embedder.fit_transform(documents)

# Access the raw embedding values via the Vector.value attribute.
first_vector = vectors[0].value

# Transform new documents (the result is also a Vector).
new_vector = embedder.transform(["This is a new document."])[0]

# Save and load the underlying Doc2Vec model.
model_path = "doc2vec.model"
embedder.save_model(model_path)
embedder.load_model(model_path)
