from swarmauri.utils.LazyLoader import LazyLoader

retriever_files = [
    ("swarmauri_community.retrievers.concrete.RedisDocumentRetriever", "RedisDocumentRetriever"),
]

for module_name, class_name in retriever_files:
    globals()[class_name] = LazyLoader(module_name, class_name)

__all__ = [class_name for _, class_name in retriever_files]
