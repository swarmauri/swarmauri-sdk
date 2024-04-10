from swarmauri.standard.metrics.base.MetricBase import MetricBase

# Implementing a StaticValueMetric class
class StaticValueMetric(MetricBase):
    """
    A static metric that always returns a fixed, predefined value.
    
    Attributes:
        name (str): The name of the metric.
        unit (str): The unit of measurement for the metric.
        _value (Any): The static value of the metric.
    """
    def __init__(self, name: str, unit: str, value):
        """
        Initialize the static metric with its name, unit, and static value.

        Args:
            name (str): The name identifier for the metric.
            unit (str): The unit of measurement for the metric.
            value: The static value for this metric.
        """
        # Initialize attributes from the base class
        super().__init__(name, unit)
        # Assign the static value
        self._value = value

    # Overriding the 'value' property to always return the static value
    @property
    def value(self):
        """
        Overridden to return the predefined static value for this metric.
        """
        return self._value