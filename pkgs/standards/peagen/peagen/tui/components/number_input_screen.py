from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label


class NumberInputScreen(ModalScreen[int | None]):
    """Prompt the user for a numeric value."""

    def __init__(self, prompt: str, initial: int) -> None:
        super().__init__()
        self.prompt = prompt
        self.initial = initial

    def compose(self) -> ComposeResult:  # pragma: no cover - UI code
        with Vertical(id="number_input_box"):
            yield Label(self.prompt)
            yield Input(
                value=str(self.initial),
                id="number_input",
                placeholder="value",
            )
            with Horizontal():
                yield Button("OK", id="submit", variant="primary")
                yield Button("Cancel", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "submit":
            value = self.query_one("#number_input", Input).value
            try:
                num = int(value)
            except Exception:
                num = None
            self.dismiss(num)
        elif event.button.id == "cancel":
            self.dismiss(None)
