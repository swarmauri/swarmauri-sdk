from swarmauri.utils._lazy_import import _lazy_import


embeddings_files = [
    ("swarmauri_community.embeddings.concrete.Doc2VecEmbedding", "Doc2VecEmbedding"),
    ("swarmauri_community.embeddings.concrete.MlmEmbedding", "MlmEmbedding"),
]

for module_name, class_name in embeddings_files:
    globals()[class_name] = _lazy_import(module_name, class_name)

__all__ = [class_name for _, class_name in embeddings_files]
