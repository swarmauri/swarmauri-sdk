from swarmauri.utils._lazy_import import _lazy_import

# List of documents names (file names without the ".py" extension) and corresponding class names
documents_files = [("swarmauri_standard.documents.Document", "Document")]

# Lazy loading of documents classes, storing them in variables
for module_name, class_name in documents_files:
    globals()[class_name] = _lazy_import(module_name, class_name)

# Adding the lazy-loaded documents classes to __all__
__all__ = [class_name for _, class_name in documents_files]
