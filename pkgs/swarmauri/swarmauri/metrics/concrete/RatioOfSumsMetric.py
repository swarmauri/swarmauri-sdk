from typing import Any
import pandas as pd

from swarmauri.metrics.base.MetricBase import MetricBase
from swarmauri.metrics.base.MetricCalculateMixin import MetricCalculateMixin

class RatioOfSumsMetric(MetricBase, MetricCalculateMixin):
    def calculate(self, data: pd.DataFrame, column_a: str, column_b: str) -> float:
        sum_a = data[column_a].sum()
        sum_b = data[column_b].sum()
        
        if sum_b == 0:
            raise ValueError(f"The sum of column '{column_b}' is zero, cannot divide by zero.")
        
        return sum_a / sum_b 