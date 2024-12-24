from typing import Any, Dict, List, Literal, Union, Optional
import pandas as pd
import numpy as np
from swarmauri_base.measurements.MeasurementBase import MeasurementBase
from swarmauri.measurements.base.MeasurementCalculateMixin import (
    MeasurementCalculateMixin,
)


class MissingnessMeasurement(MeasurementCalculateMixin, MeasurementBase):
    """
    A metric that evaluates the percentage of missing values in a dataset.

    Missingness is calculated as the ratio of missing values to total values,
    expressed as a percentage. This metric helps identify data quality issues
    and incompleteness in datasets.

    Attributes:
        type (Literal['MissingnessMeasurement']): Type identifier for the metric
        unit (str): Unit of measurement (percentage)
        value (float): Stores the calculated missingness score
        measurements (List[Optional[float]]): List of measurements to analyze
    """

    type: Literal["MissingnessMeasurement"] = "MissingnessMeasurement"
    unit: str = "%"
    measurements: List[Optional[float]] = []

    def calculate_missingness(self, data: Union[pd.DataFrame, List, Dict]) -> float:
        """
        Calculates the missingness score for different data types.

        Args:
            data: Input data which can be a pandas DataFrame, List, or Dictionary

        Returns:
            float: Missingness score as a percentage (0-100)

        Raises:
            ValueError: If an unsupported data type is provided
        """
        if isinstance(data, pd.DataFrame):
            total_values = data.size
            missing_values = data.isna().sum().sum()
        elif isinstance(data, list):
            total_values = len(data)
            missing_values = sum(1 for x in data if x is None)
        elif isinstance(data, dict):
            total_values = len(data)
            missing_values = sum(1 for v in data.values() if v is None)
        else:
            raise ValueError(
                "Unsupported data type. Please provide DataFrame, List, or Dict."
            )

        if total_values == 0:
            return 0.0

        return (missing_values / total_values) * 100

    def __call__(self, data: Union[pd.DataFrame, List, Dict], **kwargs) -> float:
        """
        Calculates and returns the missingness score for the provided data.

        Args:
            data: Input data to evaluate missingness
            **kwargs: Additional parameters (reserved for future use)

        Returns:
            float: Missingness score as a percentage (0-100)
        """
        self.value = self.calculate_missingness(data)
        return self.value

    def get_column_missingness(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate missingness scores for individual columns in a DataFrame.

        Args:
            df: Input DataFrame

        Returns:
            Dict[str, float]: Dictionary mapping column names to their missingness scores

        Raises:
            ValueError: If input is not a pandas DataFrame
        """
        if not isinstance(df, pd.DataFrame):
            raise ValueError("Input must be a pandas DataFrame")

        return {
            column: (df[column].isna().sum() / len(df) * 100) for column in df.columns
        }

    def calculate(self) -> float:
        """
        Calculate method required by MeasurementCalculateMixin.
        Uses the measurements list to calculate missingness.

        Returns:
            float: Missingness score as a percentage (0-100)
        """
        if not self.measurements:
            return 0.0

        total_values = len(self.measurements)
        missing_values = sum(1 for x in self.measurements if x is None)

        missingness = (missing_values / total_values) * 100
        self.update(missingness)
        return missingness

    def add_measurement(self, measurement: Optional[float]) -> None:
        """
        Adds a measurement to the internal list of measurements.

        Args:
            measurement (Optional[float]): A numerical value or None to be added to the list of measurements.
        """
        self.measurements.append(measurement)
