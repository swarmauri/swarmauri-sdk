from swarmauri.utils._lazy_import import _lazy_import

# List of embeddings names (file names without the ".py" extension) and corresponding class names
embeddings_files = [
    ("swarmauri.embeddings.concrete.CohereEmbedding", "CohereEmbedding"),
    ("swarmauri.embeddings.concrete.GeminiEmbedding", "GeminiEmbedding"),
    ("swarmauri.embeddings.concrete.MistralEmbedding", "MistralEmbedding"),
    ("swarmauri.embeddings.concrete.NmfEmbedding", "NmfEmbedding"),
    ("swarmauri.embeddings.concrete.OpenAIEmbedding", "OpenAIEmbedding"),
    ("swarmauri.embeddings.concrete.TfidfEmbedding", "TfidfEmbedding"),
    ("swarmauri.embeddings.concrete.VoyageEmbedding", "VoyageEmbedding"),
]

# Lazy loading of embeddings classes, storing them in variables
for module_name, class_name in embeddings_files:
    globals()[class_name] = _lazy_import(module_name, class_name)

# Adding the lazy-loaded embeddings classes to __all__
__all__ = [class_name for _, class_name in embeddings_files]
