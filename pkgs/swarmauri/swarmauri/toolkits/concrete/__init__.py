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

# List of toolkit names (file names without the ".py" extension)
toolkit_files = [
    "AccessibilityToolkit",
    "Toolkit",
]

# Lazy loading of toolkit modules, storing them in variables
for toolkit in toolkit_files:
    globals()[toolkit] = _lazy_import(f"swarmauri.toolkits.concrete.{toolkit}", toolkit)

# Adding the lazy-loaded toolkit modules to __all__
__all__ = toolkit_files
