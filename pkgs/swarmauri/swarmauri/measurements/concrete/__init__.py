from swarmauri.utils.LazyLoader import LazyLoader

# List of measurements names (file names without the ".py" extension) and corresponding class names
measurements_files = [
    (
        "swarmauri.measurements.concrete.CompletenessMeasurement",
        "CompletenessMeasurement",
    ),
    (
        "swarmauri.measurements.concrete.DistinctivenessMeasurement",
        "DistinctivenessMeasurement",
    ),
    (
        "swarmauri.measurements.concrete.FirstImpressionMeasurement",
        "FirstImpressionMeasurement",
    ),
    ("swarmauri.measurements.concrete.MeanMeasurement", "MeanMeasurement"),
    ("swarmauri.measurements.concrete.MiscMeasurement", "MiscMeasurement"),
    (
        "swarmauri.measurements.concrete.MissingnessMeasurement",
        "MissingnessMeasurement",
    ),
    (
        "swarmauri.measurements.concrete.PatternMatchingMeasurement",
        "PatternMatchingMeasurement",
    ),
    (
        "swarmauri.measurements.concrete.RatioOfSumsMeasurement",
        "RatioOfSumsMeasurement",
    ),
    ("swarmauri.measurements.concrete.StaticMeasurement", "StaticMeasurement"),
    ("swarmauri.measurements.concrete.UniquenessMeasurement", "UniquenessMeasurement"),
    ("swarmauri.measurements.concrete.ZeroMeasurement", "ZeroMeasurement"),
]

# Lazy loading of measurements classes, storing them in variables
for module_name, class_name in measurements_files:
    globals()[class_name] = LazyLoader(module_name, class_name)

# Adding the lazy-loaded measurements classes to __all__
__all__ = [class_name for _, class_name in measurements_files]
