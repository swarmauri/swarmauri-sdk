from swarmauri.utils.LazyLoader import LazyLoader

# List of state names (file names without the ".py" extension) and corresponding class names
state_files = [
    ("swarmauri.state.concrete.DictState", "DictState"),
]

# Lazy loading of state classes, storing them in variables
for module_name, class_name in state_files:
    globals()[class_name] = LazyLoader(module_name, class_name)

# Adding the lazy-loaded state classes to __all__
__all__ = [class_name for _, class_name in state_files]
