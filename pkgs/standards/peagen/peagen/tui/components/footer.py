from datetime import datetime

try:  # psutil may not be installed in minimal test env
    import psutil
except Exception:  # pragma: no cover - optional dependency
    psutil = None
from textual.reactive import reactive
from textual.widgets import Footer


class DashboardFooter(Footer):
    clock: reactive[str] = reactive("")
    metrics: reactive[str] = reactive("")
    hint: str = "Tab: switch | S: sort | F: filter | C: collapse | Esc: clear"

    def on_mount(self) -> None:
        self.set_interval(1.0, self.update_metrics)

    def update_metrics(self) -> None:
        self.clock = datetime.now().strftime("%H:%M:%S")
        if psutil:
            self.metrics = (
                f"CPU: {psutil.cpu_percent()}% | MEM: {psutil.virtual_memory().percent}%"
            )
        else:  # pragma: no cover - missing psutil
            self.metrics = "CPU: n/a | MEM: n/a"

    def render(self) -> str:
        return f"{self.clock} | {self.metrics} | {self.hint}"

