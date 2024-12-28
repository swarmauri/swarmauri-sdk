# from swarmauri.utils._lazy_import import _lazy_import

# # List of embeddings names (file names without the ".py" extension) and corresponding class names
# embeddings_files = [
#     ("swarmauri_standard.embeddings.CohereEmbedding", "CohereEmbedding"),
#     ("swarmauri_standard.embeddings.GeminiEmbedding", "GeminiEmbedding"),
#     ("swarmauri_standard.embeddings.MistralEmbedding", "MistralEmbedding"),
#     ("swarmauri_standard.embeddings.NmfEmbedding", "NmfEmbedding"),
#     ("swarmauri_standard.embeddings.OpenAIEmbedding", "OpenAIEmbedding"),
#     ("swarmauri_standard.embeddings.TfidfEmbedding", "TfidfEmbedding"),
#     ("swarmauri_standard.embeddings.VoyageEmbedding", "VoyageEmbedding"),
# ]

# # Lazy loading of embeddings classes, storing them in variables
# for module_name, class_name in embeddings_files:
#     globals()[class_name] = _lazy_import(module_name, class_name)

# # Adding the lazy-loaded embeddings classes to __all__
# __all__ = [class_name for _, class_name in embeddings_files]
