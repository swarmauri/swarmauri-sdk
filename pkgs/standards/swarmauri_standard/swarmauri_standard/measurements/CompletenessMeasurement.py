from typing import Any, Dict, List, Literal, Union
import pandas as pd
import numpy as np
from swarmauri_base.measurements.MeasurementBase import MeasurementBase


class CompletenessMeasurement(MeasurementBase):
    """
    Measurement for evaluating the completeness of a dataset or collection of values.
    Completeness is calculated as the percentage of non-missing values in the dataset.

    Attributes:
        type (Literal['CompletenessMeasurement']): Type identifier for the measurement
        unit (str): Unit of measurement (percentage)
        value (float): Stores the calculated completeness score
    """

    type: Literal["CompletenessMeasurement"] = "CompletenessMeasurement"
    unit: str = "%"  # Percentage as the unit of measurement

    def calculate_completeness(self, data: Union[pd.DataFrame, List, Dict]) -> float:
        """
        Calculates the completeness score for different data types.

        Args:
            data: Input data which can be a pandas DataFrame, List, or Dictionary

        Returns:
            float: Completeness score as a percentage (0-100)
        """
        if isinstance(data, pd.DataFrame):
            total_values = data.size
            non_missing_values = data.notna().sum().sum()
        elif isinstance(data, list):
            total_values = len(data)
            non_missing_values = sum(1 for x in data if x is not None)
        elif isinstance(data, dict):
            total_values = len(data)
            non_missing_values = sum(1 for v in data.values() if v is not None)
        else:
            raise ValueError(
                "Unsupported data type. Please provide DataFrame, List, or Dict."
            )

        if total_values == 0:
            return 0.0

        return (non_missing_values / total_values) * 100

    def __call__(self, data: Union[pd.DataFrame, List, Dict], **kwargs) -> float:
        """
        Calculates and returns the completeness score for the provided data.

        Args:
            data: Input data to evaluate completeness
            **kwargs: Additional parameters (reserved for future use)

        Returns:
            float: Completeness score as a percentage (0-100)
        """
        self.value = self.calculate_completeness(data)
        return self.value

    def get_column_completeness(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate completeness scores for individual columns in a DataFrame.

        Args:
            df: Input DataFrame

        Returns:
            Dict[str, float]: Dictionary mapping column names to their completeness scores
        """
        if not isinstance(df, pd.DataFrame):
            raise ValueError("Input must be a pandas DataFrame")

        return {
            column: (df[column].notna().sum() / len(df) * 100) for column in df.columns
        }
