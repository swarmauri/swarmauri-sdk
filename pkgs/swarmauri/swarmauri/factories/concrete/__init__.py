from swarmauri.utils.LazyLoader import LazyLoader

# List of swarms names (file names without the ".py" extension) and corresponding class names
factories_files = [
    ("swarmauri.factories.concrete.Factory", "Factory"),
    ("swarmauri.factories.concrete.AgentFactory", "AgentFactory"),
]

# Lazy loading of swarms classes, storing them in variables
for module_name, class_name in factories_files:
    globals()[class_name] = LazyLoader(module_name, class_name)

# Adding the lazy-loaded swarms classes to __all__
__all__ = [class_name for _, class_name in factories_files]
