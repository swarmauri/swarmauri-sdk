from typing import Any
import pandas as pd
from sklearn.feature_selection import mutual_info_classif
from swarmauri.metrics.base.MetricBase import MetricBase
from swarmauri.metrics.base.MetricCalculateMixin import MetricCalculateMixin

class MutualInformationMetric(MetricBase, MetricCalculateMixin):
    def calculate(self, data: pd.DataFrame, target_column: str) -> float:  # Now returns a float
        # Separate features from the target column
        features_data = data.drop(columns=[target_column])
        target_data = data[target_column]

        # Calculate mutual information
        mi = mutual_info_classif(features_data, target_data)

        # Return the average mutual information across all features
        return float(mi.mean())  # Output as a float