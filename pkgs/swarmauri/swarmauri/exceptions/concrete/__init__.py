from swarmauri.utils.LazyLoader import LazyLoader

# List of exceptions names (file names without the ".py" extension) and corresponding class names
exceptions_files = [
    ("swarmauri.exceptions.concrete.IndexErrorWithContext", "IndexErrorWithContext"),
]

# Lazy loading of exceptions classes, storing them in variables
for module_name, class_name in exceptions_files:
    globals()[class_name] = LazyLoader(module_name, class_name)

# Adding the lazy-loaded exceptions classes to __all__
__all__ = [class_name for _, class_name in exceptions_files]
