from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Center, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label


class NumberInputScreen(ModalScreen[int | None]):
    """Prompt the user for a numeric input."""

    def __init__(self, prompt: str) -> None:
        super().__init__()
        self.prompt = prompt

    def compose(self) -> ComposeResult:  # pragma: no cover - UI code
        yield Center(
            Vertical(
                Label(self.prompt, id="prompt-label"),
                Input(id="number-input"),
                Horizontal(Button("OK", id="ok"), Button("Cancel", id="cancel")),
            )
        )

    async def on_button_pressed(
        self, event: Button.Pressed
    ) -> None:  # pragma: no cover - UI code
        if event.button.id == "ok":
            value = self.query_one("#number-input", Input).value
            self.dismiss(int(value)) if value.isdigit() else self.dismiss(None)
        else:
            self.dismiss(None)
