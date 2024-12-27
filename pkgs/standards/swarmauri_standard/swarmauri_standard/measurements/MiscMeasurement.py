from typing import Any, Dict, List, Literal, Union, Optional
import pandas as pd
import numpy as np
from pydantic import Field
from swarmauri_base.measurements.MeasurementBase import MeasurementBase


class MiscMeasurement(MeasurementBase):
    """
    A measurement class that provides various basic metrics including sum, minimum,
    maximum, and string length calculations.
    """

    type: Literal["MiscMeasurement"] = "MiscMeasurement"
    unit: str = ""  # Define as a string field
    value: Any = None
    resource: Optional[str] = Field(default="measurement", frozen=True)

    def __init__(self, **data):
        super().__init__(**data)
        self._values = {
            "sum": None,
            "minimum": None,
            "maximum": None,
            "min_length": None,
            "max_length": None,
        }

    def calculate_sum(self, data: Union[pd.Series, List[Union[int, float]]]) -> float:
        """
        Calculate the sum of numerical values.

        Args:
            data: Input numerical data
        Returns:
            float: Sum of the values
        """
        if isinstance(data, pd.Series):
            result = data.sum()
        else:
            result = sum(data)

        self._values["sum"] = result
        self.value = result
        return result

    def calculate_minimum(
        self, data: Union[pd.Series, List[Union[int, float]]]
    ) -> float:
        """
        Find the minimum value in the data.

        Args:
            data: Input numerical data
        Returns:
            float: Minimum value
        """
        if isinstance(data, pd.Series):
            result = data.min()
        else:
            result = min(data)

        self._values["minimum"] = result
        self.value = result
        return result

    def calculate_maximum(
        self, data: Union[pd.Series, List[Union[int, float]]]
    ) -> float:
        """
        Find the maximum value in the data.

        Args:
            data: Input numerical data
        Returns:
            float: Maximum value
        """
        if isinstance(data, pd.Series):
            result = data.max()
        else:
            result = max(data)

        self._values["maximum"] = result
        self.value = result
        return result

    def calculate_min_length(self, data: Union[pd.Series, List[str]]) -> int:
        """
        Find the minimum string length in the data.

        Args:
            data: Input string data
        Returns:
            int: Minimum string length
        """
        if isinstance(data, pd.Series):
            result = data.str.len().min()
        else:
            result = min(len(s) for s in data)

        self._values["min_length"] = result
        self.value = result
        return result

    def calculate_max_length(self, data: Union[pd.Series, List[str]]) -> int:
        """
        Find the maximum string length in the data.

        Args:
            data: Input string data
        Returns:
            int: Maximum string length
        """
        if isinstance(data, pd.Series):
            result = data.str.len().max()
        else:
            result = max(len(s) for s in data)

        self._values["max_length"] = result
        self.value = result
        return result

    def calculate_all_numeric(
        self, data: Union[pd.Series, List[Union[int, float]]]
    ) -> Dict[str, float]:
        """
        Calculate all numerical metrics (sum, minimum, maximum) at once.

        Args:
            data: Input numerical data
        Returns:
            Dict[str, float]: Dictionary containing all numerical metrics
        """
        results = {
            "sum": self.calculate_sum(data),
            "minimum": self.calculate_minimum(data),
            "maximum": self.calculate_maximum(data),
        }
        self.value = results
        return results

    def calculate_all_string(self, data: Union[pd.Series, List[str]]) -> Dict[str, int]:
        """
        Calculate all string metrics (min_length, max_length) at once.

        Args:
            data: Input string data
        Returns:
            Dict[str, int]: Dictionary containing all string length metrics
        """
        results = {
            "min_length": self.calculate_min_length(data),
            "max_length": self.calculate_max_length(data),
        }
        self.value = results
        return results

    def __call__(self, data: Any, **kwargs) -> Dict[str, Union[float, int]]:
        """
        Main entry point for calculating measurements. Determines the type of data
        and calculates appropriate metrics.

        Args:
            data: Input data (numerical or string)
            kwargs: Additional parameters including 'metric_type' ('numeric' or 'string')
        Returns:
            Dict[str, Union[float, int]]: Dictionary containing calculated metrics
        """
        metric_type = kwargs.get("metric_type", "numeric")

        if metric_type == "numeric":
            return self.calculate_all_numeric(data)
        elif metric_type == "string":
            return self.calculate_all_string(data)
        else:
            raise ValueError("metric_type must be either 'numeric' or 'string'")
