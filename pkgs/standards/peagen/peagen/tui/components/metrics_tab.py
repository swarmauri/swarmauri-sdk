import random

from textual.widgets import Sparkline, Static


class MetricsTab(Static):
    def on_mount(self) -> None:
        self.values = [0] * 30  # Fixed-length rolling window
        self.spark = Sparkline()
        self.mount(self.spark)
        self.set_interval(1.0, self.update_spark)

    def update_spark(self) -> None:
        self.values.pop(0)
        self.values.append(random.randint(0, 100))
        self.spark.update(self.values)
