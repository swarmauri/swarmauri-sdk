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

# List of distance names (file names without the ".py" extension)
distance_files = [
    "CanberraDistance",
    "ChebyshevDistance",
    "ChiSquaredDistance",
    "CosineDistance",
    "EuclideanDistance",
    "HaversineDistance",
    "JaccardIndexDistance",
    "LevenshteinDistance",
    "ManhattanDistance",
    "MinkowskiDistance",
    "SorensenDiceDistance",
    "SquaredEuclideanDistance",
]

# Lazy loading of distance modules, storing them in variables
for distance in distance_files:
    globals()[distance] = _lazy_import(f"swarmauri.distances.concrete.{distance}", distance)

# Adding the lazy-loaded distance modules to __all__
__all__ = distance_files
