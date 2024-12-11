from swarmauri.utils._lazy_import import _lazy_import

documents_stores_files = [
    ("swarmauri_community.documents_stores.concrete.RedisDocumentStore", "RedisDocumentStore"),
]

for module_name, class_name in documents_stores_files:
    globals()[class_name] = _lazy_import(module_name, class_name)

__all__ = [class_name for _, class_name in documents_stores_files]
