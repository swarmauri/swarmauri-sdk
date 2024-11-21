from swarmauri.utils._lazy_import import _lazy_import

measurement_files = [
    ("swarmauri_community.measurements.concrete.MutualInformationMeasurement", "MutualInformationMeasurement"),
    ("swarmauri_community.measurements.concrete.TokenCountEstimatorMeasurement", "TokenCountEstimatorMeasurement"),
]

for module_name, class_name in measurement_files:
    globals()[class_name] = _lazy_import(module_name, class_name)

__all__ = [class_name for _, class_name in measurement_files]
