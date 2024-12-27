from typing import Any, Dict, List, Literal, Union
import pandas as pd
from swarmauri_base.measurements.MeasurementBase import MeasurementBase


class UniquenessMeasurement(MeasurementBase):
    """
    Measurement for evaluating the uniqueness of values in a dataset.
    Uniqueness is calculated as the percentage of distinct values relative to the total number of values.

    Attributes:
        type (Literal['UniquenessMeasurement']): Type identifier for the measurement
        unit (str): Unit of measurement (percentage)
        value (float): Stores the calculated uniqueness score
    """

    type: Literal["UniquenessMeasurement"] = "UniquenessMeasurement"
    unit: str = "%"  # Percentage as the unit of measurement

    def calculate_uniqueness(self, data: Union[pd.DataFrame, List, Dict]) -> float:
        """
        Calculates the uniqueness score for different data types.

        Args:
            data: Input data which can be a pandas DataFrame, List, or Dictionary

        Returns:
            float: Uniqueness score as a percentage (0-100)

        Raises:
            ValueError: If the input data type is not supported
        """
        if isinstance(data, pd.DataFrame):
            if data.empty:
                return 0.0
            # For DataFrame, calculate uniqueness across all columns
            total_values = data.size
            unique_values = sum(data[col].nunique() for col in data.columns)
            return (unique_values / total_values) * 100

        elif isinstance(data, list):
            if not data:
                return 0.0
            total_values = len(data)
            unique_values = len(
                set(str(x) for x in data)
            )  # Convert to strings to handle unhashable types
            return (unique_values / total_values) * 100

        elif isinstance(data, dict):
            if not data:
                return 0.0
            total_values = len(data)
            unique_values = len(
                set(str(v) for v in data.values())
            )  # Convert to strings to handle unhashable types
            return (unique_values / total_values) * 100

        else:
            raise ValueError(
                "Unsupported data type. Please provide DataFrame, List, or Dict."
            )

    def call(
        self, data: Union[pd.DataFrame, List, Dict], kwargs: Dict[str, Any] = None
    ) -> float:
        """
        Calculates and returns the uniqueness score for the provided data.

        Args:
            data: Input data to evaluate uniqueness
            kwargs: Additional parameters (reserved for future use)

        Returns:
            float: Uniqueness score as a percentage (0-100)
        """
        self.value = self.calculate_uniqueness(data)
        return self.value

    def get_column_uniqueness(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate uniqueness scores for individual columns in a DataFrame.

        Args:
            df: Input DataFrame

        Returns:
            Dict[str, float]: Dictionary mapping column names to their uniqueness scores

        Raises:
            ValueError: If input is not a pandas DataFrame
        """
        if not isinstance(df, pd.DataFrame):
            raise ValueError("Input must be a pandas DataFrame")

        return {column: (df[column].nunique() / len(df) * 100) for column in df.columns}
