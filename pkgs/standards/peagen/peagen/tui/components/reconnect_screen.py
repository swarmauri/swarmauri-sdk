from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Center, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Static


class ReconnectScreen(ModalScreen[None]):
    """Display a connection error with retry logic."""

    def __init__(self, message: str, on_retry) -> None:
        super().__init__()
        self.message = message
        self.on_retry = on_retry
        self._counter = 30

    def compose(self) -> ComposeResult:  # pragma: no cover - ui code
        yield Center(
            Vertical(
                Static(self.message, id="error-message"),
                Horizontal(
                    Button("Retry", id="retry"),
                    Button("Close", id="close"),
                ),
                Static(f"Retrying in {self._counter}s", id="timer"),
                id="reconnect-box",
            )
        )

    def on_mount(self) -> None:  # pragma: no cover - ui code
        self.set_interval(1.0, self._tick)

    def _tick(self) -> None:  # pragma: no cover - ui code
        self._counter -= 1
        timer = self.query_one("#timer", Static)
        timer.update(f"Retrying in {self._counter}s")
        if self._counter <= 0:
            self.dismiss()
            self.on_retry()

    async def on_button_pressed(
        self, event: Button.Pressed
    ) -> None:  # pragma: no cover - ui code
        if event.button.id == "retry":
            self.dismiss()
            self.on_retry()
        elif event.button.id == "close":
            self.app.exit()
