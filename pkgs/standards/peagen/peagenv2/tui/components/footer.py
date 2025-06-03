from textual.widgets import Footer
from textual.reactive import reactive
from textual.timer import Timer
from datetime import datetime
import psutil


class DashboardFooter(Footer):
    clock: reactive[str] = reactive("")
    metrics: reactive[str] = reactive("")
    hint: str = "Press [Tab] to switch tabs"

    def on_mount(self) -> None:
        self.set_interval(1.0, self.update_metrics)

    def update_metrics(self) -> None:
        self.clock = datetime.now().strftime("%H:%M:%S")
        self.metrics = f"CPU: {psutil.cpu_percent()}% | MEM: {psutil.virtual_memory().percent}%"

    def render(self) -> str:
        return f"{self.clock} | {self.metrics} | {self.hint}"
