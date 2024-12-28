from swarmauri_standard.utils._lazy_import import _lazy_import

# List of vectore_stores names (file names without the ".py" extension) and corresponding class names
vectore_stores_files = [
    ("swarmauri_standard.vector_stores.SqliteVectorStore", "SqliteVectorStore"),
    ("swarmauri_standard.vector_stores.TfidfVectorStore", "TfidfVectorStore"),
]

# Lazy loading of vectore_storess, storing them in variables
for module_name, class_name in vectore_stores_files:
    globals()[class_name] = _lazy_import(module_name, class_name)

# Adding the lazy-loaded vectore_storess to __all__
__all__ = [class_name for _, class_name in vectore_stores_files]
