from swarmauri.utils.LazyLoader import LazyLoader

# List of toolkit names (file names without the ".py" extension) and corresponding class names
toolkit_files = [
    ("swarmauri.toolkits.concrete.AccessibilityToolkit", "AccessibilityToolkit"),
    ("swarmauri.toolkits.concrete.Toolkit", "Toolkit"),
]

# Lazy loading of toolkit modules, storing them in variables
for module_name, class_name in toolkit_files:
    globals()[class_name] = LazyLoader(module_name, class_name)

# Adding the lazy-loaded toolkit modules to __all__
__all__ = [class_name for _, class_name in toolkit_files]
