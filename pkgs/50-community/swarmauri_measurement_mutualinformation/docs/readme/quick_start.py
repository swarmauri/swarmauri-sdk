import pandas as pd
from swarmauri_measurement_mutualinformation import (
    MutualInformationMeasurement,
)

frame = pd.DataFrame(
    {
        "feature_a": [0, 1, 1, 0, 1, 0],
        "feature_b": [5.1, 5.0, 4.9, 5.2, 5.1, 5.0],
        "target": [0, 1, 1, 0, 1, 0],
    }
)

measurement = MutualInformationMeasurement()
score = measurement.calculate(frame, target_column="target")
print(score)
