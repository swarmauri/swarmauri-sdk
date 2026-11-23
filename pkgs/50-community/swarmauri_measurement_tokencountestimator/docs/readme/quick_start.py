from swarmauri_measurement_tokencountestimator import (
    TokenCountEstimatorMeasurement,
)

measurement = TokenCountEstimatorMeasurement()
text = "Lorem ipsum odor amet, consectetuer adipiscing elit."
count = measurement.calculate(text)
print(count)
