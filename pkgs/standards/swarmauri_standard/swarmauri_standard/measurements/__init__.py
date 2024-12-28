# from swarmauri.utils._lazy_import import _lazy_import

# # List of measurements names (file names without the ".py" extension) and corresponding class names
# measurements_files = [
#     (
#         "swarmauri_standard.measurements.CompletenessMeasurement",
#         "CompletenessMeasurement",
#     ),
#     (
#         "swarmauri_standard.measurements.DistinctivenessMeasurement",
#         "DistinctivenessMeasurement",
#     ),
#     (
#         "swarmauri_standard.measurements.FirstImpressionMeasurement",
#         "FirstImpressionMeasurement",
#     ),
#     ("swarmauri_standard.measurements.MeanMeasurement", "MeanMeasurement"),
#     ("swarmauri_standard.measurements.MiscMeasurement", "MiscMeasurement"),
#     (
#         "swarmauri_standard.measurements.MissingnessMeasurement",
#         "MissingnessMeasurement",
#     ),
#     (
#         "swarmauri_standard.measurements.PatternMatchingMeasurement",
#         "PatternMatchingMeasurement",
#     ),
#     (
#         "swarmauri_standard.measurements.RatioOfSumsMeasurement",
#         "RatioOfSumsMeasurement",
#     ),
#     ("swarmauri_standard.measurements.StaticMeasurement", "StaticMeasurement"),
#     ("swarmauri_standard.measurements.UniquenessMeasurement", "UniquenessMeasurement"),
#     ("swarmauri_standard.measurements.ZeroMeasurement", "ZeroMeasurement"),
# ]

# # Lazy loading of measurements classes, storing them in variables
# for module_name, class_name in measurements_files:
#     globals()[class_name] = _lazy_import(module_name, class_name)

# # Adding the lazy-loaded measurements classes to __all__
# __all__ = [class_name for _, class_name in measurements_files]
