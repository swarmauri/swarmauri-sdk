from typing import Any, Dict, List, Literal, Union
import pandas as pd
import numpy as np
from swarmauri_base.measurements.MeasurementBase import MeasurementBase


class DistinctivenessMeasurement(MeasurementBase):
    """
    Measurement for evaluating the distinctiveness of a dataset or collection of values.
    Distinctiveness is calculated as the percentage of unique non-null values relative to
    the total number of non-null values in the dataset.

    Attributes:
        type (Literal['DistinctivenessMeasurement']): Type identifier for the measurement
        unit (str): Unit of measurement (percentage)
        value (float): Stores the calculated distinctiveness score
    """

    type: Literal["DistinctivenessMeasurement"] = "DistinctivenessMeasurement"
    unit: str = "%"  # Percentage as the unit of measurement

    def calculate_distinctiveness(self, data: Union[pd.DataFrame, List, Dict]) -> float:
        """
        Calculates the distinctiveness score for different data types.

        Args:
            data: Input data which can be a pandas DataFrame, List, or Dictionary

        Returns:
            float: Distinctiveness score as a percentage (0-100)
        """
        if isinstance(data, pd.DataFrame):
            # For DataFrames, calculate distinctiveness across all columns
            non_null_values = data.count().sum()
            if non_null_values == 0:
                return 0.0
            # Count unique values across all columns, excluding null values
            unique_values = sum(data[col].dropna().nunique() for col in data.columns)
            return (unique_values / non_null_values) * 100

        elif isinstance(data, list):
            # Filter out None values
            non_null_values = [x for x in data if x is not None]
            if not non_null_values:
                return 0.0
            # Calculate distinctiveness for list
            return (len(set(non_null_values)) / len(non_null_values)) * 100

        elif isinstance(data, dict):
            # Filter out None values
            non_null_values = [v for v in data.values() if v is not None]
            if not non_null_values:
                return 0.0
            # Calculate distinctiveness for dictionary values
            return (len(set(non_null_values)) / len(non_null_values)) * 100

        else:
            raise ValueError(
                "Unsupported data type. Please provide DataFrame, List, or Dict."
            )

    def call(
        self, data: Union[pd.DataFrame, List, Dict], kwargs: Dict[str, Any] = None
    ) -> float:
        """
        Calculates and returns the distinctiveness score for the provided data.

        Args:
            data: Input data to evaluate distinctiveness
            kwargs: Additional parameters (reserved for future use)

        Returns:
            float: Distinctiveness score as a percentage (0-100)
        """
        self.value = self.calculate_distinctiveness(data)
        return self.value

    def get_column_distinctiveness(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate distinctiveness scores for individual columns in a DataFrame.

        Args:
            df: Input DataFrame

        Returns:
            Dict[str, float]: Dictionary mapping column names to their distinctiveness scores
        """
        if not isinstance(df, pd.DataFrame):
            raise ValueError("Input must be a pandas DataFrame")

        return {
            column: (
                df[column].dropna().nunique() / df[column].count() * 100
                if df[column].count() > 0
                else 0.0
            )
            for column in df.columns
        }
