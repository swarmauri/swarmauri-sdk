import importlib

# Define a lazy loader function with a warning message if the module is not found
def _lazy_import(module_name, module_description=None):
    try:
        return importlib.import_module(module_name)
    except ImportError:
        # If module is not available, print a warning message
        print(f"Warning: The module '{module_description or module_name}' is not available. "
              f"Please install the necessary dependencies to enable this functionality.")
        return None

# List of metric names (file names without the ".py" extension)
metric_files = [
]

# Lazy loading of distance modules, storing them in variables
for metric in metric_files:
    globals()[metric] = _lazy_import(f"swarmauri.metrics.concrete.{metric}", metric)

# Adding the lazy-loaded metric modules to __all__
__all__ = metric_files