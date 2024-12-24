from typing import Any, Literal
import pandas as pd

from swarmauri_base.measurements.MeasurementBase import MeasurementBase
from swarmauri_base.measurements.MeasurementCalculateMixin import MeasurementCalculateMixin


class PatternMatchingMeasurement(MeasurementBase, MeasurementCalculateMixin):
    """
    A measurement class to calculate the percentage of data points that match a given pattern in a column.
    """
    unit: str = "percentage"
    type: Literal["PatternMatchingMeasurement"] = "PatternMatchingMeasurement"

    def calculate(self, data: pd.DataFrame, column: str, pattern: str) -> float:
        """
        Calculate the percentage of data points that match a given pattern in a column.

        Parameters:
            data (pd.DataFrame): The input DataFrame.
            column (str): The name of the column to match against.
            pattern (str): The pattern to match.

        Returns:
            float: The percentage of data points that match the pattern.
        """
        # Perform pattern matching
        matches = data[column].str.contains(pattern, regex=True)

        # Calculate the proportion of True values (i.e., the percentage of matches)
        return matches.mean() * 100  # Returning percentage as a float
