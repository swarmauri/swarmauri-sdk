from swarmauri.utils._lazy_import import _lazy_import

# List of exceptions names (file names without the ".py" extension) and corresponding class names
exceptions_files = [
    ("swarmauri_standard.exceptions.IndexErrorWithContext", "IndexErrorWithContext"),
]

# Lazy loading of exceptions classes, storing them in variables
for module_name, class_name in exceptions_files:
    globals()[class_name] = _lazy_import(module_name, class_name)

# Adding the lazy-loaded exceptions classes to __all__
__all__ = [class_name for _, class_name in exceptions_files]
