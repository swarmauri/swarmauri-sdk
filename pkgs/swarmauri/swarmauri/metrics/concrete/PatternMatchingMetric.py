from typing import Any
import pandas as pd

from swarmauri.metrics.base.MetricBase import MetricBase
from swarmauri.metrics.base.MetricCalculateMixin import MetricCalculateMixin


class PatternMatchingMetric(MetricBase, MetricCalculateMixin):
    def calculate(self, data: pd.DataFrame, column: str, pattern: str) -> float:
        # Perform pattern matching
        matches = data[column].str.contains(pattern, regex=True)
        
        # Calculate the proportion of True values (i.e., the percentage of matches)
        return matches.mean() * 100  # Returning percentage as a float 