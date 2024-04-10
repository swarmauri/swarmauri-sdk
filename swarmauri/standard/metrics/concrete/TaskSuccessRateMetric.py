from swarmauri.standard.metrics.base.AggregateMetricBase import AggregateMetricBase

class TaskSuccessRateMetric(AggregateMetricBase):
    """
    Metric calculating the task success rate over all attempted tasks.
    """
    
    def __init__(self):
        super().__init__(name="TaskSuccessRate", unit="percentage")
        self.total_tasks = 0
        self.successful_tasks = 0

    def add_measurement(self, measurement) -> None:
        """
        Adds a task outcome to the metrics. Measurement should be a boolean indicating task success.
        """
        self.total_tasks += 1
        if measurement:
            self.successful_tasks += 1

    def calculate(self, **kwargs) -> float:
        """
        Calculate the success rate of tasks based on the total and successful tasks.

        Returns:
            float: The success rate as a percentage.
        """
        if self.total_tasks == 0:
            return 0.0
        success_rate = (self.successful_tasks / self.total_tasks) * 100
        self.update(success_rate)
        return self.value
    
    @property
    def measurements(self):
        return {"total_tasks": self.total_tasks, "successful_tasks": self.successful_tasks} 