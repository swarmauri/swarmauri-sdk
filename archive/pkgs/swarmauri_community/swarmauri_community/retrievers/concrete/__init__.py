from swarmauri.utils._lazy_import import _lazy_import

retriever_files = [
    ("swarmauri_community.retrievers.concrete.RedisDocumentRetriever", "RedisDocumentRetriever"),
]

for module_name, class_name in retriever_files:
    globals()[class_name] = _lazy_import(module_name, class_name)

__all__ = [class_name for _, class_name in retriever_files]
