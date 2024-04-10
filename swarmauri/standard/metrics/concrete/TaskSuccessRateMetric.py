from swarmauri.standard.metrics.base.AggregateMetricBase import AggregateMetricBase

class TaskSuccessRateMetric(AggregateMetricBase):
    def __init__(self):
        super().__init__(name="Task Success Rate", unit="%")
        self.total_tasks = 0
        self.successful_tasks = 0

    def calculate(self, **kwargs) -> Any:
        if self.total_tasks == 0:
            return 0
        else:
            success_rate = (self.successful_tasks / self.total_tasks) * 100
            return success_rate

    def add_measurement(self, success: bool) -> None:
        self.total_tasks += 1
        if success:
            self.successful_tasks += 1
    
    @property
    def measurements(self):
        return {"total_tasks": self.total_tasks, "successful_tasks": self.successful_tasks} 