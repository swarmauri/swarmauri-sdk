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
    page: reactive[str] = reactive("")
    hint: str = (
        "Tab: switch | S: sort | C: collapse | Esc: clear | "
        "N/P: page | J: jump | L: limit"
    )

    def on_mount(self) -> None:
        self.set_interval(1.0, self.update_metrics)

    def set_page_info(self, current: int, total: int) -> None:
        """Update the current pagination display."""
        self.page = f"{current}/{total}" if total else f"{current}/?"

    def update_metrics(self) -> None:
        self.clock = datetime.now().strftime("%H:%M:%S")
        if psutil:
            self.metrics = f"CPU: {psutil.cpu_percent()}% | MEM: {psutil.virtual_memory().percent}%"
        else:  # pragma: no cover - missing psutil
            self.metrics = "CPU: n/a | MEM: n/a"

    def render(self) -> str:
        page_part = f"Page {self.page} | " if self.page else ""
        return f"{self.clock} | {self.metrics} | {page_part}{self.hint}"
