from swarmauri.standard.metrics.base.ThresholdMetricBase import ThresholdMetricBase

class ImpressionAtKMetric(ThresholdMetricBase):
    def __init__(self, k: int):
        super().__init__(name="Impression at K", unit="count", k=k)
    
    def calculate(self, impressions, **kwargs):
        if not isinstance(impressions, list):
            raise ValueError("Impressions should be provided as a list")
        
        k_impressions = impressions[:self._k] if len(impressions) >= self._k else impressions

        self._value = len([imp for imp in k_impressions if imp > 0])
        return self._value

    def reset(self):
        self._value = 0
    
    def update(self, value):
        raise NotImplementedError("This Metric does not support update operation directly.")
    
    def __call__(self, **kwargs):
        """
        Retrieves the current value of the metric.
        
        Returns:
            The current value of the metric if calculated; otherwise, triggers a calculation.
        """
        if 'impressions' in kwargs:
            return self.calculate(kwargs['impressions'])
        return self._value