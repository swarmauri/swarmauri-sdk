from swarmauri.utils.LazyLoader import LazyLoader


embeddings_files = [
    ("swarmauri_community.embeddings.concrete.Doc2VecEmbedding", "Doc2VecEmbedding"),
    ("swarmauri_community.embeddings.concrete.MlmEmbedding", "MlmEmbedding"),
]

for module_name, class_name in embeddings_files:
    globals()[class_name] = LazyLoader(module_name, class_name)

__all__ = [class_name for _, class_name in embeddings_files]
