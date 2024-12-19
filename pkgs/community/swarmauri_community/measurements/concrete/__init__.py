from swarmauri.utils.LazyLoader import LazyLoader

measurement_files = [
    ("swarmauri_community.measurements.concrete.MutualInformationMeasurement", "MutualInformationMeasurement"),
    ("swarmauri_community.measurements.concrete.TokenCountEstimatorMeasurement", "TokenCountEstimatorMeasurement"),
]

for module_name, class_name in measurement_files:
    globals()[class_name] = LazyLoader(module_name, class_name)

__all__ = [class_name for _, class_name in measurement_files]
