from typing import Any, Literal
import tiktoken
from swarmauri.measurements.base.MeasurementBase import MeasurementBase
from swarmauri.measurements.base.MeasurementCalculateMixin import (
    MeasurementCalculateMixin,
)


class TokenCountEstimatorMeasurement(MeasurementBase, MeasurementCalculateMixin):
    """
    A measurement class to estimate the number of tokens in a given text.
    """

    unit: str = "tokens"
    type: Literal["TokenCountEstimatorMeasurement"] = "TokenCountEstimatorMeasurement"

    def calculate(self, text: str, encoding="cl100k_base") -> int:
        """
        Calculate the number of tokens in the given text.
        Args:
            text (str): The input text to calculate token count for.
        Returns:
            int: The number of tokens in the text, or None if an error occurs.
        """
        try:
            encoding = tiktoken.get_encoding(encoding)
        except ValueError as e:
            print(f"Error: {e}")
            return None

        tokens = encoding.encode(text)
        return len(tokens)
