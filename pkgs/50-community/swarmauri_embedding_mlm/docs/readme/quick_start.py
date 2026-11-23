from swarmauri_embedding_mlm import MlmEmbedding

documents = [
    "Swarmauri components compose agents, memory, and tools.",
    "Masked language models can adapt to domain terminology.",
]

embedder = MlmEmbedding(
    embedding_name="distilbert-base-uncased",
    batch_size=8,
    learning_rate=3e-5,
)

embedder.fit(documents)
vectors = embedder.transform(
    [
        "Agents retrieve context from vector stores.",
        "Domain adaptation improves local vocabulary coverage.",
    ]
)

print(len(vectors))
print(vectors[0].value[:5])
