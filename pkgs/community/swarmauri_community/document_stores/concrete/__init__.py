from swarmauri.utils.LazyLoader import LazyLoader

documents_stores_files = [
    ("swarmauri_community.documents_stores.concrete.RedisDocumentStore", "RedisDocumentStore"),
]

for module_name, class_name in documents_stores_files:
    globals()[class_name] = LazyLoader(module_name, class_name)

__all__ = [class_name for _, class_name in documents_stores_files]
