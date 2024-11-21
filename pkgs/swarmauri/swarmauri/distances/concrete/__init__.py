from swarmauri.utils._lazy_import import _lazy_import

# List of distances names (file names without the ".py" extension) and corresponding class names
distances_files = [
    ("swarmauri.distances.concrete.CanberraDistance", "CanberraDistance"),
    ("swarmauri.distances.concrete.ChebyshevDistance", "ChebyshevDistance"),
    ("swarmauri.distances.concrete.ChiSquaredDistance", "ChiSquaredDistance"),
    ("swarmauri.distances.concrete.CosineDistance", "CosineDistance"),
    ("swarmauri.distances.concrete.EuclideanDistance", "EuclideanDistance"),
    ("swarmauri.distances.concrete.HaversineDistance", "HaversineDistance"),
    ("swarmauri.distances.concrete.JaccardIndexDistance", "JaccardIndexDistance"),
    ("swarmauri.distances.concrete.LevenshteinDistance", "LevenshteinDistance"),
    ("swarmauri.distances.concrete.ManhattanDistance", "ManhattanDistance"),
    ("swarmauri.distances.concrete.MinkowskiDistance", "MinkowskiDistance"),
    ("swarmauri.distances.concrete.SorensenDiceDistance", "SorensenDiceDistance"),
    (
        "swarmauri.distances.concrete.SquaredEuclideanDistance",
        "SquaredEuclideanDistance",
    ),
]

# Lazy loading of distances classes, storing them in variables
for module_name, class_name in distances_files:
    globals()[class_name] = _lazy_import(module_name, class_name)

# Adding the lazy-loaded distances classes to __all__
__all__ = [class_name for _, class_name in distances_files]
