from typing import Any, Literal
import pandas as pd
from sklearn.feature_selection import mutual_info_classif
from swarmauri.measurements.base.MeasurementBase import MeasurementBase
from swarmauri.measurements.base.MeasurementCalculateMixin import (
    MeasurementCalculateMixin,
)


class MutualInformationMeasurement(MeasurementBase, MeasurementCalculateMixin):
    """
    A Measurement class to calculate mutual information between features and a target column in a given dataset.

    This class computes the mutual information between each feature in a DataFrame (excluding the target column)
    and the target column itself, and returns the average mutual information score.
    """

    type: Literal["MutualInformationMeasurement"] = "MutualInformationMeasurement"
    unit: str = "bits"

    def calculate(self, data: pd.DataFrame, target_column: str) -> float:
        """
        Calculate the average mutual information between the features and the target column.

        Parameters:
        - data (pd.DataFrame): A DataFrame containing both the features and the target column.

        - target_column (str) The name of the target column in the DataFrame.

        Returns:
        - float: The average mutual information across all feature columns.
        """
        # Separate features from the target column
        features_data = data.drop(columns=[target_column])
        target_data = data[target_column]

        # Calculate mutual information
        mi = mutual_info_classif(features_data, target_data)

        # Return the average mutual information across all features
        return float(mi.mean())  # Output as a float
