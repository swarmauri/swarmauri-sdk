from swarmauri.utils._lazy_import import _lazy_import

# List of toolkit names (file names without the ".py" extension) and corresponding class names
toolkit_files = [
    ("swarmauri_standard.toolkits.AccessibilityToolkit", "AccessibilityToolkit"),
    ("swarmauri_standard.toolkits.Toolkit", "Toolkit"),
]

# Lazy loading of toolkit modules, storing them in variables
for module_name, class_name in toolkit_files:
    globals()[class_name] = _lazy_import(module_name, class_name)

# Adding the lazy-loaded toolkit modules to __all__
__all__ = [class_name for _, class_name in toolkit_files]
