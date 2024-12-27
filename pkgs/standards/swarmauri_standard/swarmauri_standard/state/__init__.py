from swarmauri.utils._lazy_import import _lazy_import

# List of state names (file names without the ".py" extension) and corresponding class names
state_files = [
    ("swarmauri_standard.state.DictState", "DictState"),
]

# Lazy loading of state classes, storing them in variables
for module_name, class_name in state_files:
    globals()[class_name] = _lazy_import(module_name, class_name)

# Adding the lazy-loaded state classes to __all__
__all__ = [class_name for _, class_name in state_files]
