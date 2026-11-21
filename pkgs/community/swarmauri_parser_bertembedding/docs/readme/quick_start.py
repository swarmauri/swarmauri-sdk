from swarmauri_parser_bertembedding import BERTEmbeddingParser

parser = BERTEmbeddingParser(parser_model_name="bert-base-uncased")
documents = parser.parse(
    [
        "Swarmauri agents cooperate over shared memory.",
        "Dense embeddings power semantic search.",
    ]
)

for document in documents:
    embedding = document.metadata["embedding"]
    print(document.content)
    print(len(embedding), embedding[:5])
