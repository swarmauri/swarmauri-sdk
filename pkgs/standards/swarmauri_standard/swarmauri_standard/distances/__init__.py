from swarmauri_standard.utils._lazy_import import _lazy_import

# List of distances names (file names without the ".py" extension) and corresponding class names
distances_files = [
    ("swarmauri_standard.distances.CanberraDistance", "CanberraDistance"),
    ("swarmauri_standard.distances.ChebyshevDistance", "ChebyshevDistance"),
    ("swarmauri_standard.distances.ChiSquaredDistance", "ChiSquaredDistance"),
    ("swarmauri_standard.distances.CosineDistance", "CosineDistance"),
    ("swarmauri_standard.distances.EuclideanDistance", "EuclideanDistance"),
    ("swarmauri_standard.distances.HaversineDistance", "HaversineDistance"),
    ("swarmauri_standard.distances.JaccardIndexDistance", "JaccardIndexDistance"),
    ("swarmauri_standard.distances.LevenshteinDistance", "LevenshteinDistance"),
    ("swarmauri_standard.distances.ManhattanDistance", "ManhattanDistance"),
    ("swarmauri_standard.distances.MinkowskiDistance", "MinkowskiDistance"),
    ("swarmauri_standard.distances.SorensenDiceDistance", "SorensenDiceDistance"),
    (
        "swarmauri_standard.distances.SquaredEuclideanDistance",
        "SquaredEuclideanDistance",
    ),
]

# Lazy loading of distances classes, storing them in variables
for module_name, class_name in distances_files:
    globals()[class_name] = _lazy_import(module_name, class_name)

# Adding the lazy-loaded distances classes to __all__
__all__ = [class_name for _, class_name in distances_files]
