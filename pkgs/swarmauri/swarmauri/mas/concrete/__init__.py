from swarmauri.utils.LazyLoader import LazyLoader

# List of mas name (file names without the ".py" extension) and corresponding class names
mas_files = [
    (
        "swarmauri.mas.concrete.CentralizedMas",
        "CentralizedMas",
    ),
]

# Lazy loading of mas classes, storing them in variables
for module_name, class_name in mas_files:
    globals()[class_name] = LazyLoader(module_name, class_name)

# Adding the lazy-loaded mas classes to __all__
__all__ = [class_name for _, class_name in mas_files]
