import statistics
from swarmauri.standard.metrics.base.AggregateMetricBase import AggregateMetricBase

class TimeOnTaskMetric(AggregateMetricBase):
    """
    Metric to calculate the average time users spend on a given task.
    """
    def __init__(self, name="Time on Task", unit="seconds"):
        super().__init__(name, unit)

    def calculate(self, **kwargs):
        """
        Calculate the average time on task based on the collected measurements.
        """
        if not self.measurements:
            return 0
        return statistics.mean(self.measurements)

    def add_measurement(self, seconds: float) -> None:
        """
        Adds a measurement of time (in seconds) that a user spent on a task.
        """
        if seconds < 0:
            raise ValueError("Time on task cannot be negative.")
        super().add_measurement(seconds)